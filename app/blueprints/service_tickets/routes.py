from .schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_ticket_schema,
    add_part_to_ticket_schema
)
from app.models import (
    Customer,
    Service_Ticket,
    Mechanic,
    Inventory,
    Parts_Per_Ticket,
    db
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_tickets_bp
from app.extensions import limiter, cache
from app.utils.util import roles_required


# POST a new service ticket
@service_tickets_bp.route("/", methods=["POST"])
@roles_required("mechanic",)
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
@limiter.limit("100 per hour")
@roles_required("mechanic",)
def get_all_service_tickets():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Service_Ticket)
        tickets = db.paginate(query, page=page, per_page=per_page)

        return service_tickets_schema.jsonify(tickets), 200

    except:
        query = select(Service_Ticket)
        service_tickets = db.session.execute(query).scalars().all()
        
        return service_tickets_schema.jsonify(service_tickets), 200


# GET a single service ticket by ID
@service_tickets_bp.route("/<int:id>", methods=["GET"])
@limiter.limit("100 per hour")
@roles_required("mechanic",)
def get_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    service_ticket = db.session.execute(query).scalars().first()

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    return service_ticket_schema.jsonify(service_ticket), 200


# PUT update mechanics assigned to a service ticket by service ticket ID
@service_tickets_bp.route("/<int:id>/edit", methods=["PUT"])
@roles_required("mechanic",)
def update_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    service_ticket = db.session.execute(query).scalars().first()

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    try:
        ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for mechanic_id in ticket_edits["add_mechanic_ids"]:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    for mechanic_id in ticket_edits["remove_mechanic_ids"]:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()

    return service_ticket_schema.jsonify(service_ticket), 200

# POST add parts to a service ticket via ID
@service_tickets_bp.route("/<int:ticket_id>/parts", methods=["POST"])
@roles_required("mechanic",)
def add_part_to_ticket(ticket_id):
    try:
        data = add_part_to_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    service_ticket = db.session.get(Service_Ticket, ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service ticket not found."}), 404

    part = db.session.get(Inventory, data["part_id"])

    if not part:
        return jsonify({"error": "Inventory part not found."}), 404

    if data["part_quantity"] <= 0:
        return jsonify({"error": "part_quantity must be greater than 0."}), 400

    existing_part = db.session.execute(
        select(Parts_Per_Ticket).where(
            Parts_Per_Ticket.ticket_id == ticket_id,
            Parts_Per_Ticket.part_id == data["part_id"]
        )
    ).scalars().first()

    if existing_part:
        existing_part.part_quantity += data["part_quantity"]
    else:
        part_assignment = Parts_Per_Ticket(
            ticket_id=ticket_id,
            part_id=data["part_id"],
            part_quantity=data["part_quantity"]
        )

        db.session.add(part_assignment)

    db.session.commit()

    return service_ticket_schema.jsonify(service_ticket), 200

# PUT update the quantity of a part on a ticket
@service_tickets_bp.route("/<int:ticket_id>/parts/<int:part_id>", methods=["PUT"])
@roles_required("mechanic",)
def update_ticket_part_quantity(ticket_id, part_id):
    data = request.json

    if "part_quantity" not in data:
        return jsonify({"error": "part_quantity is required."}), 400

    if data["part_quantity"] <= 0:
        return jsonify({"error": "part_quantity must be greater than 0."}), 400

    ticket_part = db.session.execute(
        select(Parts_Per_Ticket).where(
            Parts_Per_Ticket.ticket_id == ticket_id,
            Parts_Per_Ticket.part_id == part_id
        )
    ).scalars().first()

    if not ticket_part:
        return jsonify({"error": "Part is not assigned to this service ticket."}), 404

    ticket_part.part_quantity = data["part_quantity"]

    db.session.commit()

    service_ticket = db.session.get(Service_Ticket, ticket_id)

    return service_ticket_schema.jsonify(service_ticket), 200

# DELETE a part from a service ticket
@service_tickets_bp.route("/<int:ticket_id>/parts/<int:part_id>", methods=["DELETE"])
@roles_required("mechanic",)
def remove_part_from_ticket(ticket_id, part_id):
    ticket_part = db.session.execute(
        select(Parts_Per_Ticket).where(
            Parts_Per_Ticket.ticket_id == ticket_id,
            Parts_Per_Ticket.part_id == part_id
        )
    ).scalars().first()

    if not ticket_part:
        return jsonify({"error": "Part is not assigned to this service ticket."}), 404

    db.session.delete(ticket_part)
    db.session.commit()

    service_ticket = db.session.get(Service_Ticket, ticket_id)

    return service_ticket_schema.jsonify(service_ticket), 200

# DELETE a service ticket by ID
@service_tickets_bp.route("/<int:id>", methods=["DELETE"])
@limiter.limit("5 per day")
@roles_required("mechanic",)
def delete_service_ticket(id):
    query = select(Service_Ticket).where(Service_Ticket.id == id)
    service_ticket = db.session.execute(query).scalars().first()

    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({"message": f"Service ticket id: {id}, deleted successfully."}), 200