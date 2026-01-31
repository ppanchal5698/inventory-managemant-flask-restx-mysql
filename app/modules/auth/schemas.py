# Auth schemas

from marshmallow import Schema, fields, validate, post_load


class UserSchema(Schema):
    """User serialization schema."""
    user_id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    first_name = fields.Str(required=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=True, validate=validate.Length(max=100))
    email = fields.Email(required=True)
    phone = fields.Str(validate=validate.Length(max=20))
    role = fields.Str(validate=validate.OneOf(['admin', 'manager', 'staff', 'viewer']))
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """User creation schema."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=True, validate=validate.Length(max=100))
    email = fields.Email(required=True)
    phone = fields.Str(validate=validate.Length(max=20))
    role = fields.Str(validate=validate.OneOf(['admin', 'manager', 'staff', 'viewer']), load_default='staff')


class LoginSchema(Schema):
    """Login schema."""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PasswordChangeSchema(Schema):
    """Password change schema."""
    current_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
login_schema = LoginSchema()
password_change_schema = PasswordChangeSchema()
