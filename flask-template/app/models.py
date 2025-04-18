from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    Fullname = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(15))
    Address = db.Column(db.String(255))

    # Flask-Login requires these methods
    def get_id(self):
        return str(self.UserID)

class Category(db.Model):
    __tablename__ = 'categories'
    CategoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CategoryName = db.Column(db.String(100), unique=True, nullable=False)

class Product(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(255))
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    Stock = db.Column(db.Integer, nullable=False)
    CategoryID = db.Column(db.Integer, db.ForeignKey('categories.CategoryID'))
    ImageURL = db.Column(db.String(255))

class Order(db.Model):
    __tablename__ = 'orders'
    OrderID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    TotalAmount = db.Column(db.Numeric(10, 2), nullable=False)
    Status = db.Column(db.String(100), default='Pending')
    ShippingAddress = db.Column(db.String(255))
    OrderDate = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    items = db.relationship('OrderItem', backref='order')
    user = db.relationship('User', backref='orders')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    OrderItemID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('orders.OrderID'))
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'))
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationship with Product
    product = db.relationship('Product')

class Cart(db.Model):
    __tablename__ = 'cart'
    CartID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    ProductID = db.Column(db.Integer, db.ForeignKey('products.ProductID'))
    Quantity = db.Column(db.Integer, nullable=False)