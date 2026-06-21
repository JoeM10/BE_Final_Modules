from .schemas import (
    customer_schema,
    customers_schema,
    login_schema,
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, Service_Ticket, db
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, roles_required
from app.blueprints.service_tickets.schemas import service_tickets_schema


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
        token = encode_token(user_id=customer.id, role="customer")

        response = {
            "status": "success",
            "message": "Successfully logged in.",
            "token": token
        }

        return jsonify(response), 200
    else:
        return jsonify({"LoginError": "Invalid email or password!"}), 401

# POST a new customer
@customers_bp.route("/", methods=["POST"])
@limiter.limit("20 per hour")
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

# GET all tickets associated with the currently logged in customer
@customers_bp.route("/my-tickets", methods=["GET"])
@limiter.limit("50 per hour")
@roles_required("customer",)
@cache.cached(timeout=60)
def get_my_tickets(current_user):
    customer_id = current_user["id"]

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    query = select(Service_Ticket).where(Service_Ticket.customer_id == customer_id)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200

# GET all customers
@customers_bp.route("/", methods=["GET"])
@roles_required("mechanic", "admin")
def get_customers(current_user):
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)

        return customers_schema.jsonify(customers), 200

    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()

        return customers_schema.jsonify(customers), 200

# GET a single customer by ID
@customers_bp.route("/<int:id>", methods=["GET"])
@roles_required("mechanic", "admin")
def get_customer(current_user, id):
    customer = db.session.get(Customer, id)

    if customer:
        return customer_schema.jsonify(customer), 200

    return jsonify({"error": "Customer not found."}), 404

# PUT update a customer by ID for customer use only
@customers_bp.route("/update_account", methods=["PUT"])
@limiter.limit("10 per day")
@roles_required("customer")
def update_customer(current_user):
    customer_id = current_user["id"]

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "email" in data:
        existing_email = db.session.execute(
            select(Customer).where(
                Customer.email == data["email"],
                Customer.id != customer.id
            )
        ).scalars().first()

        if existing_email:
            return jsonify({"error": "Email already associated with an account."}), 400

    if "phone" in data:
        existing_phone = db.session.execute(
            select(Customer).where(
                Customer.phone == data["phone"],
                Customer.id != customer.id
            )
        ).scalars().first()

        if existing_phone:
            return jsonify({"error": "Phone already associated with an account."}), 400

    for key, value in data.items():
        setattr(customer, key, value)

    db.session.commit()

    return customer_schema.jsonify(customer), 200

# PUT update a customer by ID for non-customer use only
@customers_bp.route("/<int:id>", methods=["PUT"])
@roles_required("mechanic", "admin")
def mechanic_update_customer(current_user, id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Prevent duplicate email when updating email
    if "email" in data:
        existing_email = db.session.execute(
            select(Customer).where(
                Customer.email == data["email"],
                Customer.id != customer.id
            )
        ).scalars().first()

        if existing_email:
            return jsonify({"error": "Email already associated with an account."}), 400

    # Prevent duplicate phone when updating phone
    if "phone" in data:
        existing_phone = db.session.execute(
            select(Customer).where(
                Customer.phone == data["phone"],
                Customer.id != customer.id
            )
        ).scalars().first()

        if existing_phone:
            return jsonify({"error": "Phone already associated with an account."}), 400

    for key, value in data.items():
        setattr(customer, key, value)

    db.session.commit()

    return customer_schema.jsonify(customer), 200

# DELETE a customer by ID for customers only
@customers_bp.route("/delete_account", methods=["DELETE"])
@limiter.limit("10 per day")
@roles_required("customer",)
def delete_current_customer(current_user):
    customer_id = current_user["id"]

    customer = db.session.get(Customer, int(customer_id))

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    if customer.tickets:
        return jsonify({
            "error": "Cannot delete customer because they have service tickets.",
            "message": "Please contact an Employee for assistance with deleting your account."
        }), 409

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": f"Customer {customer_id} deleted successfully."}), 200

# DELETE a customer by ID for non-customers only
@customers_bp.route("/<int:id>", methods=["DELETE"])
@roles_required("mechanic", "admin")
def delete_customer(current_user, id):
    customer = db.session.get(Customer, int(id))

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    if customer.tickets:
        return jsonify({
            "error": "Cannot delete customer because they have service tickets.",
            "message": "Delete this customer's service tickets first, or keep the customer record for service history."
        }), 409

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted successfully."}), 200