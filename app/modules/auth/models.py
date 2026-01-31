# User model

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.database import BaseModel
from app.extensions import db, login_manager


class User(UserMixin, BaseModel):
    """User model for authentication and authorization."""
    __tablename__ = 'users'

    user_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('admin', 'manager', 'staff', 'viewer', name='user_role'),
                     nullable=False, default='staff')
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    purchase_orders = db.relationship('PurchaseOrder', backref='creator',
                                       foreign_keys='PurchaseOrder.created_by', lazy='dynamic')
    sales_orders = db.relationship('SalesOrder', backref='creator',
                                    foreign_keys='SalesOrder.created_by', lazy='dynamic')

    def get_id(self):
        """Return user_id for Flask-Login."""
        return str(self.user_id)

    @property
    def full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize user to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))
