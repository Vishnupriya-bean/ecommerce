from flask import Blueprint, request, jsonify
from database import db
from models.user import User
from bcrypt import hashpw, gensalt, checkpw
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity



auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# REGISTER ----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data:
        return jsonify({"error": "Data required"}), 400
    user_name=data.get("user_name")
    email = data.get("email")
    password = data.get("password")
    delivery_address=data.get('delivery_address')

    if not user_name or not email or not password or not delivery_address:
        return jsonify({
        "error": "user_name, email, password and delivery_address are required"
    }), 400


   
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = hashpw(password.encode(), gensalt()).decode()

   
    user = User(user_name=user_name,
    email=email,
    password_hash=hashed_password,
    delivery_address=delivery_address
)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

    return jsonify({"message": "User registered successfully"}), 201


# LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data:
        return jsonify({"error": "Data required"}), 400 
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": "user"}
    )

    return jsonify({
    "message": "Login successful",
    "access_token": access_token
    }), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({
        "message": "Logged out successfully"
    }), 200






