from flask import Blueprint, request, jsonify
from database import db
from models.cart import Cart
from models.product import Product
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
cart_bp = Blueprint("cart", __name__, url_prefix="/cart")

# add product to cart...........................

@cart_bp.route("", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()  
    data = request.json
    if not data:
        return jsonify({"error": "Data required"}), 400

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not user_id or not product_id:
        return jsonify({"error": "user_id and product_id are required"}), 400

    # verify user exists
    if not User.query.get(user_id):
        return jsonify({"error": "User not found"}), 404

    # verify product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # check if product already in cart
    cart_item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({"message": "Product added to cart"}), 201



#get cart items for user

@cart_bp.route("/<int:user_id>", methods=["GET"])
def get_cart(user_id):

    if not User.query.get(user_id):
        return jsonify({"error": "User not found"}), 404

    cart_items = Cart.query.filter_by(user_id=user_id).all()

    result = []
    for item in cart_items:
        product = Product.query.get(item.product_id)

        result.append({
            "cart_id": item.id,
            "product_id": product.id,
            "product_name": product.product_name,
            "price": product.price,
            "quantity": item.quantity,
            "image_url": product.image_url
        })

    return jsonify({
        "count": len(result),
        "cart_items": result
    }), 200


# Remove item from cart

@cart_bp.route("/<int:cart_id>", methods=["DELETE"])
def remove_cart_item(cart_id):
    cart_item = Cart.query.get(cart_id)

    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({"message": "Item removed from cart"}), 200
