from app.extensions import ma
from app.models import Customer
from marshmallow import ValidationError, fields, validate


def not_blank(value):
    if not value.strip():
        raise ValidationError("Field cannot be blank.")

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    # Validation
    name = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])
    email = fields.Email(required=True, validate=[not_blank, validate.Length(max=255)])
    phone = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])
    password = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])

    class Meta:
        model = Customer

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude=["name", "phone"])
