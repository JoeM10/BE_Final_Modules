from app.extensions import ma
from app.models import Mechanic, Service_Ticket
from marshmallow import ValidationError, fields, validate


def not_blank(value):
    if not value.strip():
        raise ValidationError("Field cannot be blank.")

class MechanicServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Ticket

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    service_tickets = fields.Nested(MechanicServiceTicketSchema, many=True, dump_only=True)

    # Validation
    name = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])
    email = fields.Email(required=True, validate=[not_blank, validate.Length(max=255)])
    phone = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])
    salary = fields.Float(required=True, validate=validate.Range(min=0))
    password = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])

    class Meta:
        model = Mechanic
        load_only = ("password",)    

class MechanicLoginSchema(ma.Schema):
    email = fields.Email(required=True, validate=not_blank)
    password = fields.String(required=True, validate=not_blank, load_only=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_login_schema = MechanicLoginSchema()
