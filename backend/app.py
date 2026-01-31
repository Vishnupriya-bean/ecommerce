from flask import Flask,jsonify
from database import db
from config import Config
from models.product import Product
from data.products_data import products_list
app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

from flask_cors import CORS
CORS(app,orgins=['http://localhost:3000'] )

from routes import auth_bp, product_bp, cart_bp, order_bp

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(order_bp)

from flask_jwt_extended import JWTManager
jwt = JWTManager(app)

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/")
def home():
        return "E-commerce backend running!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            for item in products_list:
                product = Product(**item)
                db.session.add(product)
            db.session.commit()
            print("✅ Products inserted into database")
        else:
            print("ℹ️ Products already exist, skipping insert")
   
    app.run(debug=True)

