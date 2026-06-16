from .schemas import inventory_schema, inventory_schemas
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, Service_Ticket, Mechanic, Inventory, db
from . import inventory_bp
from app.extensions import cache

# POST a new inventory item
@inventory_bp.route("/", methods=["POST"])
def create_inventory_item():
    try:
        data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_inventory_item = Inventory(item_name=data["item_name"], price=data["price"])

    db.session.add(new_inventory_item)
    db.session.commit()

    return inventory_schema.jsonify(new_inventory_item), 201

# GET all inventory items
@inventory_bp.route("/", methods=["GET"])
def get_all_inventory_items():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Inventory)
        items = db.paginate(query, page=page, per_page=per_page)

        return inventory_schemas.jsonify(items), 200

    except:
        query = select(Inventory)
        items = db.session.execute(query).scalars().all()
        
        return inventory_schemas.jsonify(items), 200


# GET a single inventory item by ID
@inventory_bp.route("/<int:id>", methods=["GET"])
def get_inventory_item(id):
    query = select(Inventory).where(Inventory.id == id)
    item = db.session.execute(query).scalars().first()

    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    return inventory_schema.jsonify(item), 200

# PUT update an inventory item by ID
@inventory_bp.route("/<int:id>", methods=["PUT"])
def update_inventory_item(id):
    query = select(Inventory).where(Inventory.id == id)
    inventory_item = db.session.execute(query).scalars().first()

    if not inventory_item:
        return jsonify({"error": "Item not found"}), 404
    
    try:
        data = inventory_schema.load(request.json, partial=True)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in data.items():
        setattr(inventory_item, key, value)

    db.session.commit()

    return inventory_schema.jsonify(inventory_item), 200

# DELETE a inventory item by ID
@inventory_bp.route("/<int:id>", methods=["DELETE"])
def delete_inventory_item(id):
    query = select(Inventory).where(Inventory.id == id)
    inventory_item = db.session.execute(query).scalars().first()

    if not inventory_item:
        return jsonify({"error": "Service ticket not found"}), 404
    
    db.session.delete(inventory_item)
    db.session.commit()

    return jsonify({"message": f"Inventory item id: {id}, deleted successfully."}), 200

# # PUT update mechanics assigned to a service ticket by service ticket ID
# @service_tickets_bp.route("/<int:id>/edit", methods=["PUT"])
# def update_service_ticket(id):
#     query = select(Service_Ticket).where(Service_Ticket.id == id)
#     service_ticket = db.session.execute(query).scalars().first()

#     if not service_ticket:
#         return jsonify({"error": "Service ticket not found"}), 404

#     try:
#         ticket_edits = edit_service_ticket_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400

#     for mechanic_id in ticket_edits["add_mechanic_ids"]:
#         query = select(Mechanic).where(Mechanic.id == mechanic_id)
#         mechanic = db.session.execute(query).scalars().first()

#         if mechanic and mechanic not in service_ticket.mechanics:
#             service_ticket.mechanics.append(mechanic)

#     for mechanic_id in ticket_edits["remove_mechanic_ids"]:
#         query = select(Mechanic).where(Mechanic.id == mechanic_id)
#         mechanic = db.session.execute(query).scalars().first()

#         if mechanic and mechanic in service_ticket.mechanics:
#             service_ticket.mechanics.remove(mechanic)

#     db.session.commit()

#     return service_ticket_schema.jsonify(service_ticket), 200