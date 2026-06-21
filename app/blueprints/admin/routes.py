import os
from flask import request, jsonify
from marshmallow import ValidationError
from . import admin_bp
from .schemas import admin_login_schema
from app.utils.util import encode_token

@admin_bp.route("/login", methods=["POST"])
def admin_login():
    try:
        credentials = admin_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    admin_email = os.getenv("TEST_ADMIN_EMAIL")
    admin_password = os.getenv("TEST_ADMIN_PASSWORD")

    if not admin_email:
        raise RuntimeError("TEST_ADMIN_EMAIL environment variable must be set.")

    if not admin_password:
        raise RuntimeError("TEST_ADMIN_PASSWORD environment variable must be set.")

    if credentials["email"] == admin_email and credentials["password"] == admin_password:
        token = encode_token(user_id=0, role="admin")

        return jsonify({
            "status": "success",
            "message": "Admin successfully logged in.",
            "token": token
        }), 200

    return jsonify({"LoginError": "Invalid email or password."}), 401