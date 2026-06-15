from app.extensions import ma
from app.models import Mechanic, Service_Ticket
from marshmallow import fields

class MechanicServiceTicketShema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Ticket

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    service_tickets = fields.Nested(MechanicServiceTicketShema, many=True, dump_only=True)


    class Meta:
        model = Mechanic
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)