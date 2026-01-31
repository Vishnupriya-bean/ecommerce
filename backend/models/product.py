from database import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
