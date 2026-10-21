from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff', 'customer'
    client_profile = db.relationship('Client', backref='user', uselist=False, cascade='all, delete-orphan')


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    orders = db.relationship('Commande', backref='client', lazy=True, order_by='Commande.created_at.desc()')

    @property
    def total_spent(self):
        return sum(o.total_price for o in self.orders if o.status != 'Cancelled')


class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='Pizza')  # 'Top Offre', 'Pizza', 'Dessert', 'Boisson'
    photo_url = db.Column(db.String(200))
    base_price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    order_items = db.relationship('OrderItem', backref='pizza', lazy=True)


class Topping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, default=0.0)


class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    status = db.Column(db.String(20), default='New')  # 'New', 'Confirmed', 'Preparing', 'Done', 'Cancelled'
    order_type = db.Column(db.String(20))  # 'Delivery', 'Pickup'
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='commande', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Paiement', backref='commande', uselist=False, cascade='all, delete-orphan')
    delivery_info = db.relationship('PizzaLivraison', backref='commande', uselist=False, cascade='all, delete-orphan')
    facture = db.relationship('Facture', backref='commande', uselist=False, cascade='all, delete-orphan')

    @property
    def subtotal(self):
        total = 0.0
        for item in self.items:
            if item.pizza:
                total += item.pizza.base_price * item.quantity
        return total if total > 0 else self.total_price

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    customizations = db.Column(db.String(200))


class Paiement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20))  # 'Cash', 'Card'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    cash_details = db.relationship('Cash', backref='paiement', uselist=False, cascade='all, delete-orphan')


class Cash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paiement_id = db.Column(db.Integer, db.ForeignKey('paiement.id'), nullable=False)
    amount_received = db.Column(db.Float)
    change_given = db.Column(db.Float)


class PizzaLivraison(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    neighborhood = db.Column(db.String(100))
    delivery_fee = db.Column(db.Float, default=0.0)


class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey('commande.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content_html = db.Column(db.Text)
