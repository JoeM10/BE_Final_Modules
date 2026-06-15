from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required


# Customer Login
@customers_bp.route("/login", methods=["POST"])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials["email"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully loggin in.",
            "token": token
        }

        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password!"})

# POST a new customer
@customers_bp.route("/", methods=["POST"])
@limiter.limit("10 per day")
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == data["email"])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_customer = Customer(**data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

# GET all customers
@customers_bp.route("/", methods=["GET"])
@limiter.limit("100 per hour")
@cache.cached(timeout=60)
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)

# GET a single customer by ID
@customers_bp.route("/<int:id>", methods=["GET"])
@limiter.limit("100 per hour")
@cache.cached(timeout=60)
def get_customer(id):
    customer = db.session.get(Customer, id)

    if customer:
        return customer_schema.jsonify(customer), 200

    return jsonify({"error": "Customer not found."}), 404

# PUT update a customer by ID
@customers_bp.route("/<int:id>", methods=["PUT"])
@limiter.limit("10 per day")
@token_required
def update_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE a customer by ID
@customers_bp.route("/", methods=["DELETE"])
@limiter.limit("5 per day")
@token_required
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer id: {id}, deleted successfully."}), 200