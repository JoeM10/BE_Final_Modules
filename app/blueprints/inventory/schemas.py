from app.extensions import ma
from app.models import Inventory, Parts_Per_Ticket
from marshmallow import fields

class PartsAssignedToTicket(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parts_Per_Ticket
        fields = ("ticket_id", "part_quantity")

class InventorySchema(ma.SQLAlchemyAutoSchema):
    tickets_assigned = fields.Nested(PartsAssignedToTicket, many=True, dump_only=True)

    class Meta:
        model = Inventory
        include_fk = True

inventory_schema = InventorySchema()
inventory_schemas = InventorySchema(many=True)