from app.extensions import ma
from marshmallow import ValidationError, fields


def not_blank(value):
    if not value.strip():
        raise ValidationError("Field cannot be blank.")


class AdminLoginSchema(ma.Schema):
    email = fields.Email(required=True, validate=not_blank)
    password = fields.String(required=True, validate=not_blank, load_only=True)


admin_login_schema = AdminLoginSchema()
