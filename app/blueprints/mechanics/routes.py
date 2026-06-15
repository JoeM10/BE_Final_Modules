from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp
from app.extensions import limiter, cache

# POST a new mechanic
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == data["email"])
    existing_mechanic = db.session.execute(query).scalars().all()

    if existing_mechanic:
        return jsonify({"error": "Mechanic with this email already exists"}), 400

    mechanic = Mechanic(**data)
    db.session.add(mechanic)
    db.session.commit()

    return jsonify(mechanic_schema.dump(mechanic)), 201

# GET all mechanics
@mechanics_bp.route("/", methods=["GET"])
@limiter.limit("100 per hour")
@cache.cached(timeout=60)
def get_all_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return jsonify(mechanics_schema.dump(mechanics)), 200

# GET a single mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["GET"])
@limiter.limit("100 per hour")
@cache.cached(timeout=60)
def get_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    return jsonify(mechanic_schema.dump(mechanic)), 200

# PUT update a mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(mechanic, key, value)

    db.session.commit()

    return jsonify(mechanic_schema.dump(mechanic)), 200

# GET a sorted list of mechanics by amount of tickets worked on
@mechanics_bp.route("/total_tickets", methods=["GET"])
def total_tickets():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key= lambda mechanic: len(mechanic.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics)

# DELETE a mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["DELETE"])
@limiter.limit("5 per day")
def delete_mechanic(id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": f"Mechanic {id}, deleted successfully"}), 200
