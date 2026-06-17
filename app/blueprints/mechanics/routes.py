from .schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from app.models import Mechanic, db
from app.extensions import limiter, cache
from app.utils.util import encode_token, roles_required
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp

# Mechanic Login
@mechanics_bp.route("/login", methods=["POST"])
def mechanic_login():
    try:
        credentials = mechanic_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    email = credentials["email"]
    password = credentials["password"]

    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id, "mechanic")

        return jsonify({
            "status": "success",
            "message": f"Mechanic {mechanic.name} logged in successfully",
            "token": token
        }), 200

    return jsonify({"message": "Invalid email or password."}), 401

# POST a new mechanic
@mechanics_bp.route("/", methods=["POST"])
@roles_required("admin",)
def create_mechanic(current_user):
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
@roles_required("mechanic", "admin")
def get_all_mechanics(current_user):
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)

        return mechanics_schema.jsonify(mechanics), 200

    except:
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()

        return jsonify(mechanics_schema.dump(mechanics)), 200

# GET a single mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["GET"])
@limiter.limit("100 per hour")
@roles_required("mechanic", "admin")
def get_mechanic(current_user, id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    return jsonify(mechanic_schema.dump(mechanic)), 200

# PUT update a mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["PUT"])
@roles_required("mechanic", "admin")
def update_mechanic(current_user, id):
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
@roles_required("mechanic", "admin")
def total_tickets(current_user):
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key= lambda mechanic: len(mechanic.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200

# DELETE a mechanic by ID
@mechanics_bp.route("/<int:id>", methods=["DELETE"])
@limiter.limit("5 per day")
@roles_required("admin",)
def delete_mechanic(current_user, id):
    query = select(Mechanic).where(Mechanic.id == id)
    mechanic = db.session.execute(query).scalars().first()

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": f"Mechanic {id}, deleted successfully"}), 200
