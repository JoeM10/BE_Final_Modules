from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from jose import jwt
import jose
import os

SECRET_KEY = os.getenv("PY_JOSE_TOKEN")
SECRET_KEY_RENDER = os.getenv("SECRET_KEY_RENDER") or "super secret secrets"

def encode_token(user_id, role): #using unique pieces of info to make our tokens user specific
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        "iat": datetime.now(timezone.utc), #Issued at
        "sub":  str(user_id), #This needs to be a string or the token will be malformed and won't be able to be decoded.
        "role": role
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"message": "Token is missing!"}), 401

            if not auth_header.startswith("Bearer "):
                return jsonify({"message": "Invalid authorization header."}), 401

            token = auth_header.split(" ", 1)[1]

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                user_id = data["sub"]
                role = data.get("role")

                if role not in allowed_roles:
                    return jsonify({
                        "message": "You are not authorized to access this route."
                    }), 403

            except jose.exceptions.ExpiredSignatureError:
                return jsonify({"message": "Token has expired!"}), 401

            except jose.exceptions.JWTError:
                return jsonify({"message": "Invalid token!"}), 401

            current_user = {
                "id": int(user_id),
                "role": role
            }

            return f(current_user, *args, **kwargs)

        return decorated

    return decorator