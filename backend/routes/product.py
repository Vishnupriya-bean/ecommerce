from flask import Blueprint, jsonify
from models.product import Product

product_bp = Blueprint("products", __name__, url_prefix="/products")

@product_bp.route("", methods=["GET"])
def get_all_products():
    products = Product.query.all()

    product_list = [
        {
            "id": product.id,
            "product_name": product.product_name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image_url": product.image_url
        }
        for product in products
    ]

    return jsonify({
        "count": len(product_list),
        "products": product_list
    }), 200


@product_bp.route("/<int:product_id>", methods=["GET"])
def get_single_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify({
        "id": product.id,
        "product_name": product.product_name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "image_url": product.image_url
    }), 200
