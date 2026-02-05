# Extensions module

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_restx import Api
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session
from asyncio import current_task
from redis.asyncio import Redis

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from threading import get_ident

class Base(DeclarativeBase):
    """Base class for SQLAlchemy 2.0 models."""
    pass

class AsyncSQLAlchemy(SQLAlchemy):
    """Async wrapper for Flask-SQLAlchemy."""

    def __init__(self, model_class=Base, **kwargs):
        super().__init__(model_class=model_class, **kwargs)
        self._async_engine = None
        self._async_session_factory = None

    def init_app(self, app):
        """Initialize Async Engine and Session."""
        # Create Async Engine
        self._async_engine = create_async_engine(
            app.config['SQLALCHEMY_DATABASE_URI'],
            echo=app.config.get('SQLALCHEMY_ECHO', False),
            pool_pre_ping=True
        )

        # Create Async Session Factory
        self._async_session_factory = async_sessionmaker(
            self._async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

        # Overwrite self.session with Async Scoped Session
        # In tests with pytest-asyncio, using current_task for scopefunc can be stable
        # provided the event loop is consistent.

        # Use asyncio.current_task for scopefunc
        self.session = async_scoped_session(
            self._async_session_factory,
            scopefunc=current_task
        )

        # We also need to register teardown
        # FIXME: This causes issues with pytest-asyncio because Flask tries to run
        # this async function synchronously using asgiref.sync.AsyncToSync,
        # which fails if an event loop is already running.
        # For now, we rely on manual cleanup or Flask's async request handling in production.
        # app.teardown_appcontext(self.shutdown_session)

    async def shutdown_session(self, exception=None):
        """Remove session on teardown."""
        # self.session is now the async session
        await self.session.remove()

    @property
    def engine(self):
        """Proxy to the async engine."""
        return self._async_engine


# Initialize SQLAlchemy with the custom Async class
db = AsyncSQLAlchemy(model_class=Base)
migrate = Migrate()
cache = Cache() # Keep for legacy sync compat if needed, but we prefer async redis
jwt = JWTManager()
redis_client = None # Initialized in create_app

# Flask-RESTX API
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Type in the "Value" input box below: "**Bearer &lt;JWT&gt;**"'
    }
}

api = Api(
    title='Inventory Management System API',
    version='1.0',
    description='Async REST API for Inventory Management System',
    doc='/docs',
    prefix='/api',
    authorizations=authorizations,
    security='Bearer Auth'
)
