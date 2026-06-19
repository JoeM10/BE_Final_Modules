from app.extensions import ma
from app.models import Inventory, Parts_Per_Ticket
from marshmallow import ValidationError, fields, validate


def not_blank(value):
    if not value.strip():
        raise ValidationError("Field cannot be blank.")

class PartsAssignedToTicket(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parts_Per_Ticket
        fields = ("ticket_id", "part_quantity")
        include_fk = True

class InventorySchema(ma.SQLAlchemyAutoSchema):
    service_tickets_for_part = fields.Nested(PartsAssignedToTicket, many=True, dump_only=True)

    # Validation
    item_name = fields.String(required=True, validate=[not_blank, validate.Length(max=255)])
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        model = Inventory
        include_fk = True


inventory_schema = InventorySchema()
inventory_schemas = InventorySchema(many=True)
