import random
from datetime import datetime, timedelta
from app import app, ensure_default_users
from models import db, User, Client, Pizza, Commande, OrderItem, Paiement, Cash, PizzaLivraison, Facture
from werkzeug.security import generate_password_hash

# Realistic Moroccan Data
FIRST_NAMES = ["Karim", "Youssef", "Fatima", "Zineb", "Omar", "Hamza", "Leyla", "Sami", "Driss", "Khadija", "Hassan", "Meriem"]
LAST_NAMES = ["Bennani", "Alaoui", "Tazi", "Idrissi", "Mansouri", "Chraibi", "Fassi", "Zouhair", "Lahlou", "El Amrani"]
NEIGHBORHOODS = ["Gauthier", "Maarif", "Bourgogne", "Racine", "Anfa", "Oasis", "Belvédère", "Sidi Maarouf", "Ain Diab"]
STREETS = ["Rue Taha Hussein", "Boulevard Zerktouni", "Rue Molière", "Boulevard d'Anfa", "Rue de Rome", "Avenue 2 Mars"]


def seed_random_data(count=15):
    with app.app_context():
        ensure_default_users()

        pizzas = Pizza.query.all()
        if not pizzas:
            print("No pizzas found. Running seed_menu first...")
            from seed_menu import seed_data
            seed_data()
            pizzas = Pizza.query.all()

        print(f"Seeding {count} random Moroccan clients and orders...")

        for _ in range(count):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f"{first} {last}"
            phone = f"06{random.randint(10000000, 99999999)}"
            neighborhood = random.choice(NEIGHBORHOODS)
            address = f"{random.randint(1, 200)}, {random.choice(STREETS)}, {neighborhood}"

            user = User.query.filter_by(username=phone).first()
            if not user:
                user = User(
                    username=phone,
                    password_hash=generate_password_hash('guest'),
                    role='customer'
                )
                db.session.add(user)
                db.session.flush()

                client = Client(
                    user_id=user.id,
                    full_name=full_name,
                    phone=phone,
                    address=address
                )
                db.session.add(client)
                db.session.flush()
            else:
                client = user.client_profile

            for _ in range(random.randint(1, 3)):
                order_type = random.choice(['Delivery', 'Pickup'])
                status = random.choice(['New', 'Confirmed', 'Preparing', 'Done'])

                days_ago = random.randint(0, 6)
                hours_ago = random.randint(0, 23)
                created_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)

                order_items_list = random.sample(pizzas, random.randint(1, min(4, len(pizzas))))
                subtotal = 0.0

                new_order = Commande(
                    client_id=client.id,
                    status=status,
                    order_type=order_type,
                    total_price=0.0,
                    created_at=created_at
                )
                db.session.add(new_order)
                db.session.flush()

                for pizza in order_items_list:
                    qty = random.randint(1, 2)
                    item_price = pizza.base_price * qty
                    subtotal += item_price

                    oi = OrderItem(
                        commande_id=new_order.id,
                        pizza_id=pizza.id,
                        quantity=qty
                    )
                    db.session.add(oi)

                delivery_fee = 0.0 if (subtotal >= 60 or order_type == 'Pickup') else 10.0
                total = subtotal + delivery_fee
                new_order.total_price = total

                payment = Paiement(
                    commande_id=new_order.id,
                    amount=total,
                    method=random.choice(['Cash', 'Card']),
                    timestamp=created_at
                )
                db.session.add(payment)
                db.session.flush()

                if payment.method == 'Cash':
                    cash = Cash(paiement_id=payment.id, amount_received=total, change_given=0.0)
                    db.session.add(cash)

                if order_type == 'Delivery':
                    dl = PizzaLivraison(
                        commande_id=new_order.id,
                        address=address,
                        neighborhood=neighborhood,
                        delivery_fee=delivery_fee
                    )
                    db.session.add(dl)

                inv_num = f"INV-{created_at.strftime('%Y%m%d')}-{new_order.id:04d}"
                if not Facture.query.filter_by(invoice_number=inv_num).first():
                    facture = Facture(
                        commande_id=new_order.id,
                        invoice_number=inv_num,
                        created_at=created_at,
                        content_html=f"Facture {inv_num} - Client: {full_name} - Total: {total:.2f} DH"
                    )
                    db.session.add(facture)

        db.session.commit()
        print("Successfully seeded random Moroccan data!")


if __name__ == "__main__":
    seed_random_data()
