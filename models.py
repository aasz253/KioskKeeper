from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

CATEGORIES = ["Airtime", "Electricity Tokens", "Milk", "Bread", "Others"]

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit_price = db.Column(db.Float, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False, default=5)

    transactions = db.relationship("Transaction", backref="product", lazy=True, cascade="all, delete-orphan")

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def total_value(self):
        return self.quantity * self.unit_price

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "reorder_level": self.reorder_level,
            "is_low_stock": self.is_low_stock,
            "total_value": self.total_value,
        }


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Unknown",
            "type": self.type,
            "quantity": self.quantity,
            "date": self.date.isoformat(),
        }
