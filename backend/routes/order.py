from flask import Blueprint, request, jsonify
from database import db
from models.order import Order
from models.order_item import OrderItem
from models.cart import Cart
from models.product import Product
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
order_bp = Blueprint("orders", __name__, url_prefix="/orders")

# --------------------------------------------------
# PLACE ORDER
# --------------------------------------------------
@order_bp.route("", methods=["POST"])
@jwt_required
def place_order():
    data = request.json
    if not data:
        return jsonify({"error": "Data required"}), 400

    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    try:
        # 🔹 Validate user
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 🔹 Get cart items
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return jsonify({"error": "Cart is empty"}), 400

        total_amount = 0

        # 🔹 STEP 1: Validate stock & calculate total
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if not product:
                return jsonify({"error": "Product not found"}), 404

            if product.stock < item.quantity:
                return jsonify({
                    "error": f"Insufficient stock for {product.product_name}"
                }), 400

            total_amount += product.price * item.quantity

        # 🔹 STEP 2: Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount
        )
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        # 🔹 STEP 3: Create order items & reduce stock
        for item in cart_items:
            product = Product.query.get(item.product_id)

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price   # price at purchase time
            )
            db.session.add(order_item)

            # reduce stock
            product.stock -= item.quantity

        # 🔹 STEP 4: Clear cart
        for item in cart_items:
            db.session.delete(item)

        # 🔹 STEP 5: Commit transaction
        db.session.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total_amount": total_amount
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Order error:", e)
        return jsonify({"error": "Order failed"}), 500


# --------------------------------------------------
# GET USER ORDER HISTORY
# --------------------------------------------------
@order_bp.route("/<int:user_id>", methods=["GET"])
def get_orders(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    orders = Order.query.filter_by(user_id=user_id).all()

    result = []
    for order in orders:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()

        items = []
        for item in order_items:
            product = Product.query.get(item.product_id)
            items.append({
                "product_name": product.product_name,
                "price_at_purchase": item.price_at_purchase,
                "quantity": item.quantity,
                "image_url": product.image_url
            })

        result.append({
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": items
        })

    return jsonify({
        "count": len(result),
        "orders": result
    }), 200
