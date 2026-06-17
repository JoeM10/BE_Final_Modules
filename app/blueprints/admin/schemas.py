from app.extensions import ma
from marshmallow import fields


class AdminLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


admin_login_schema = AdminLoginSchema()