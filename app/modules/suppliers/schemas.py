# Supplier schemas

from marshmallow import Schema, fields, validate


class SupplierSchema(Schema):
    """Supplier serialization schema."""
    supplier_id = fields.Int(dump_only=True)
    supplier_name = fields.Str(required=True, validate=validate.Length(max=150))
    contact_person = fields.Str(validate=validate.Length(max=100))
    email = fields.Email()
    phone = fields.Str(validate=validate.Length(max=20))
    address = fields.Str()
    city = fields.Str(validate=validate.Length(max=50))
    state = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50), load_default='USA')
    postal_code = fields.Str(validate=validate.Length(max=20))
    tax_id = fields.Str(validate=validate.Length(max=50))
    payment_terms = fields.Str(validate=validate.Length(max=100))
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class SupplierCreateSchema(Schema):
    """Supplier creation schema."""
    supplier_name = fields.Str(required=True, validate=validate.Length(max=150))
    contact_person = fields.Str(validate=validate.Length(max=100))
    email = fields.Email()
    phone = fields.Str(validate=validate.Length(max=20))
    address = fields.Str()
    city = fields.Str(validate=validate.Length(max=50))
    state = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50), load_default='USA')
    postal_code = fields.Str(validate=validate.Length(max=20))
    tax_id = fields.Str(validate=validate.Length(max=50))
    payment_terms = fields.Str(validate=validate.Length(max=100))


supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)
supplier_create_schema = SupplierCreateSchema()
