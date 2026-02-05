# Auth API endpoints using Flask-RESTX

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from app.modules.auth.services import AuthService
from app.modules.auth.schemas import (
    UserCreate, LoginRequest, PasswordChange
)
from app.core.utils import api_response, require_role, async_route

auth_ns = Namespace('auth', description='Authentication operations')

# API Models for Swagger documentation
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

user_model = auth_ns.model('User', {
    'user_id': fields.Integer(readonly=True),
    'username': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'phone': fields.String(),
    'role': fields.String(),
    'is_active': fields.Boolean(readonly=True),
    'created_at': fields.DateTime(readonly=True)
})

user_create_model = auth_ns.model('UserCreate', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'phone': fields.String(),
    'role': fields.String(default='staff')
})

password_change_model = auth_ns.model('PasswordChange', {
    'current_password': fields.String(required=True),
    'new_password': fields.String(required=True)
})


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('user_login')
    @async_route
    async def post(self):
        """User login endpoint."""
        try:
            data = LoginRequest.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        user = await AuthService.authenticate(data.username, data.password)
        if user:
            # Create JWT tokens
            access_token = create_access_token(identity=str(user.user_id), additional_claims={'role': user.role})
            refresh_token = create_refresh_token(identity=str(user.user_id))

            return api_response(data={
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, message='Login successful')

        return api_response(message='Invalid credentials', status_code=401)


@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc('user_logout')
    @jwt_required()
    @async_route
    async def post(self):
        """User logout endpoint."""
        # Client should discard token.
        # Ideally, blacklist token in Redis here.
        return api_response(message='Logged out successfully')


@auth_ns.route('/me')
class CurrentUser(Resource):
    @auth_ns.doc('get_current_user')
    @jwt_required()
    @async_route
    async def get(self):
        """Get current authenticated user."""
        user_id = get_jwt_identity()
        user = await AuthService.get_user_by_id(int(user_id))
        if not user:
             return api_response(message='User not found', status_code=404)
        return api_response(data=user.to_dict())


@auth_ns.route('/users')
class UserList(Resource):
    @auth_ns.doc('list_users')
    @require_role('admin', 'manager')
    @async_route
    async def get(self):
        """Get all users."""
        users = await AuthService.get_all_users()
        return api_response(data=[u.to_dict() for u in users])

    @auth_ns.expect(user_create_model)
    @auth_ns.doc('create_user')
    @require_role('admin')
    @async_route
    async def post(self):
        """Create a new user."""
        try:
            data = UserCreate.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)
        
        if await AuthService.get_user_by_username(data.username):
            return api_response(message='Username already exists', status_code=400)
        if await AuthService.get_user_by_email(data.email):
            return api_response(message='Email already exists', status_code=400)
        
        # Pydantic model to dict
        user_data = data.model_dump()

        user = await AuthService.create_user(**user_data)
        return api_response(data=user.to_dict(), message='User created', status_code=201)


@auth_ns.route('/users/<int:user_id>')
class UserDetail(Resource):
    @auth_ns.doc('get_user')
    @require_role('admin', 'manager')
    @async_route
    async def get(self, user_id):
        """Get user by ID."""
        user = await AuthService.get_user_by_id(user_id)
        if not user:
            return api_response(message='User not found', status_code=404)
        return api_response(data=user.to_dict())

    @auth_ns.doc('update_user')
    @require_role('admin')
    @async_route
    async def put(self, user_id):
        """Update user."""
        user = await AuthService.get_user_by_id(user_id)
        if not user:
            return api_response(message='User not found', status_code=404)
        
        data = request.get_json()
        user = await AuthService.update_user(user, **data)
        return api_response(data=user.to_dict(), message='User updated')


@auth_ns.route('/change-password')
class ChangePassword(Resource):
    @auth_ns.expect(password_change_model)
    @auth_ns.doc('change_password')
    @jwt_required()
    @async_route
    async def post(self):
        """Change current user's password."""
        try:
            data = PasswordChange.model_validate(request.get_json())
        except Exception as e:
            return api_response(message=str(e), status_code=400)

        user_id = get_jwt_identity()
        user = await AuthService.get_user_by_id(int(user_id))
        
        if not user.check_password(data.current_password):
            return api_response(message='Current password is incorrect', status_code=400)
        
        await AuthService.change_password(user, data.new_password)
        return api_response(message='Password changed successfully')
