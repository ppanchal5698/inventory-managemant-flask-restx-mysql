# Customer schemas

from marshmallow import Schema, fields, validate


class CustomerSchema(Schema):
    """Customer serialization schema."""
    customer_id = fields.Int(dump_only=True)
    customer_name = fields.Str(required=True, validate=validate.Length(max=150))
    contact_person = fields.Str(validate=validate.Length(max=100))
    email = fields.Email()
    phone = fields.Str(validate=validate.Length(max=20))
    address = fields.Str()
    city = fields.Str(validate=validate.Length(max=50))
    state = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50), load_default='USA')
    postal_code = fields.Str(validate=validate.Length(max=20))
    tax_id = fields.Str(validate=validate.Length(max=50))
    credit_limit = fields.Decimal(places=2, allow_none=True, validate=validate.Range(min=0))
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CustomerCreateSchema(Schema):
    """Customer creation schema."""
    customer_name = fields.Str(required=True, validate=validate.Length(max=150))
    contact_person = fields.Str(validate=validate.Length(max=100))
    email = fields.Email()
    phone = fields.Str(validate=validate.Length(max=20))
    address = fields.Str()
    city = fields.Str(validate=validate.Length(max=50))
    state = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50), load_default='USA')
    postal_code = fields.Str(validate=validate.Length(max=20))
    tax_id = fields.Str(validate=validate.Length(max=50))
    credit_limit = fields.Decimal(places=2, allow_none=True, validate=validate.Range(min=0))


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_create_schema = CustomerCreateSchema()
