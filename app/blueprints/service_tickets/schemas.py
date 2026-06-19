from app.extensions import ma
from app.models import Service_Ticket, Mechanic, Parts_Per_Ticket, Inventory
from marshmallow import ValidationError, fields, validate


def not_blank(value):
    if not value.strip():
        raise ValidationError("Field cannot be blank.")


class MechanicsOnTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        fields = ("id", "name")


class InventoryOnTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        fields = ("id", "item_name", "price")


class PartsUsedSchema(ma.SQLAlchemyAutoSchema):
    part = fields.Nested(InventoryOnTicketSchema, dump_only=True)

    class Meta:
        model = Parts_Per_Ticket
        include_fk = True
        fields = ("id", "ticket_id", "part_id", "part_quantity", "part")


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested(MechanicsOnTicketSchema, many=True, dump_only=True)
    parts_used = fields.Nested(PartsUsedSchema, many=True, dump_only=True)

    # Validation
    VIN = fields.String(required=True, validate=[not_blank, validate.Length(max=50)])
    service_date = fields.Date(required=True)
    service_desc = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])
    customer_id = fields.Integer(required=True, validate=validate.Range(min=1))

    class Meta:
        model = Service_Ticket
        include_fk = True


class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)


class AddPartToTicketSchema(ma.Schema):
    part_id = fields.Int(required=True)
    part_quantity = fields.Int(required=True)


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
add_part_to_ticket_schema = AddPartToTicketSchema()
