from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, Service_Ticket, db
from . import service_tickets_bp

# POST a new service ticket
@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, data["customer_id"])

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    new_service_ticket = Service_Ticket(**data)

    db.session.add(new_service_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_service_ticket), 201

# GET all service tickets
@service_tickets_bp.route("/", methods=["GET"])
def get_all_service_tickets():
    query = select(Service_Ticket)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200

# GET a single service ticket by ID
@service_tickets_bp.route("/<int:id>", methods=["GET"])
def get_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    service_ticket = db.session.execute(query).scalars().first()

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    return service_ticket_schema.jsonify(service_ticket), 200

# PUT update a service ticket by ID
@service_tickets_bp.route("/<int:id>", methods=["PUT"])
def update_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    service_ticket = db.session.execute(query).scalars().first()

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    try:
        data = service_ticket_schema.load(request.json, partial=True)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in data.items():
        setattr(service_ticket, key, value)

    db.session.commit()

    return service_ticket_schema.jsonify(service_ticket), 200

# DELETE a service ticket by ID
@service_tickets_bp.route("/<int:id>", methods=["DELETE"])
def delete_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    service_ticket = db.session.execute(query).scalars().first()

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({"message": f"Service ticket id: {id}, deleted successfully."}), 200
