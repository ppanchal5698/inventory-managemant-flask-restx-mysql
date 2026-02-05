# Changelog

## [Unreleased] - 2024-10-24

### Added
- **Async Support**: Complete rewrite of the application to use Flask 3.x Async + SQLAlchemy 2.0 Async + `aiomysql`/`aiosqlite`.
- **Authentication**: Replaced Flask-Login with `Flask-JWT-Extended`. Added JWT-based auth endpoints (`/auth/login`, `/auth/refresh`).
- **Validation**: Replaced Marshmallow with `Pydantic v2` for strict request/response validation.
- **Infrastructure**: Added `Dockerfile` (multi-stage), `docker-compose.yml`, and GitHub Actions CI workflow.
- **Caching**: Implemented Redis caching for high-read endpoints (Catalog, Stock).
- **Testing**: Added `tests/test_backend.py` for comprehensive End-to-End testing of the async API. Added `pytest-asyncio` support.
- **Pagination/Search**: Added `SearchQuery` and `PaginationQuery` Pydantic models for list endpoints.

### Changed
- **Database Models**: Updated all models to use SQLAlchemy 2.0 `Mapped` and `mapped_column` syntax. Removed dynamic relationships.
- **Service Layer**: Converted all services to Async. Added explicit `refresh` logic to handle async session object lifecycles safely.
- **API Routes**: Wrapped all Flask-RESTX routes with `@async_route` to support async handlers.
- **Configuration**: Updated `config.py` to use `pydantic-settings` (implied or manual env var handling) and strict environment separation.
- **Dependencies**: Updated `pyproject.toml` and `requirements.txt` with async ecosystem packages.

### Fixed
- **Security**: Moved all secrets to environment variables. Enforced stricter input validation.
- **Performance**: Added eager loading (`selectinload`) to critical relationships (Orders -> Items) to prevent N+1 queries.
- **Bugs**: Fixed numerous issues related to session management, lazy loading in async contexts, and proper error handling.

### Removed
- **Flask-Login**: Removed in favor of stateless JWT authentication.
- **Sync DB Drivers**: Removed `pymysql`/`mysqldb` in favor of async drivers.
