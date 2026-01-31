# Auth routes

from flask import request
from flask_login import login_user, logout_user, login_required, current_user

from app.modules.auth import auth_bp
from app.modules.auth.services import AuthService
from app.modules.auth.schemas import (
    user_schema, users_schema, user_create_schema, 
    login_schema, password_change_schema
)
from app.core.utils import api_response, require_role


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    user = AuthService.authenticate(data['username'], data['password'])
    if user:
        login_user(user)
        return api_response(data=user.to_dict(), message='Login successful')
    return api_response(message='Invalid credentials', status_code=401)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout endpoint."""
    logout_user()
    return api_response(message='Logged out successfully')


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user."""
    return api_response(data=current_user.to_dict())


@auth_bp.route('/users', methods=['GET'])
@login_required
@require_role('admin', 'manager')
def get_users():
    """Get all users."""
    users = AuthService.get_all_users()
    return api_response(data=[u.to_dict() for u in users])


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@require_role('admin', 'manager')
def get_user(user_id):
    """Get user by ID."""
    user = AuthService.get_user_by_id(user_id)
    if not user:
        return api_response(message='User not found', status_code=404)
    return api_response(data=user.to_dict())


@auth_bp.route('/users', methods=['POST'])
@login_required
@require_role('admin')
def create_user():
    """Create a new user."""
    data = request.get_json()
    errors = user_create_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    # Check if username or email already exists
    if AuthService.get_user_by_username(data['username']):
        return api_response(message='Username already exists', status_code=400)
    if AuthService.get_user_by_email(data['email']):
        return api_response(message='Email already exists', status_code=400)
    
    user = AuthService.create_user(**data)
    return api_response(data=user.to_dict(), message='User created', status_code=201)


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@require_role('admin')
def update_user(user_id):
    """Update user."""
    user = AuthService.get_user_by_id(user_id)
    if not user:
        return api_response(message='User not found', status_code=404)
    
    data = request.get_json()
    user = AuthService.update_user(user, **data)
    return api_response(data=user.to_dict(), message='User updated')


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change current user's password."""
    data = request.get_json()
    errors = password_change_schema.validate(data)
    if errors:
        return api_response(message=errors, status_code=400)
    
    if not current_user.check_password(data['current_password']):
        return api_response(message='Current password is incorrect', status_code=400)
    
    AuthService.change_password(current_user, data['new_password'])
    return api_response(message='Password changed successfully')
