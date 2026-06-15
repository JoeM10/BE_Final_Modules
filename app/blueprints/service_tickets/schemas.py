from app.extensions import ma
from app.models import Service_Ticket, Mechanic
from marshmallow import fields

class MechanicsOnTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        fields = ("id", "name")

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested(MechanicsOnTicketSchema, many=True, dump_only=True)

    class Meta:
        model = Service_Ticket
        include_fk = True

class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()