from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_premium = db.Column(db.Boolean, default=False)
    # Add fields related to your payment gateway (e.g., customer ID, subscription ID)
    # payment_gateway_customer_id = db.Column(db.String(255), nullable=True)
    # payment_gateway_subscription_id = db.Column(db.String(255), nullable=True)

    items = db.relationship('Item', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    category = db.Column(db.String(64))
    image_url = db.Column(db.String(255)) # URL to the image
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Item {self.name}>'