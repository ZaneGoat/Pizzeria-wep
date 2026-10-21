from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Client, Pizza, Topping, Commande, OrderItem, Paiement, Cash, PizzaLivraison, Facture
from sqlalchemy import func, or_
from datetime import datetime, timedelta, date
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chef_amin_pizzeria_secret_key_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pizzeria.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'

VALID_ORDER_STATUSES = ['New', 'Confirmed', 'Preparing', 'Done', 'Cancelled']


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


def ensure_default_users():
    """Ensure default admin and staff accounts exist."""
    db.create_all()
    changed = False
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        changed = True
    if not User.query.filter_by(username='staff').first():
        staff = User(
            username='staff',
            password_hash=generate_password_hash('staff123'),
            role='staff'
        )
        db.session.add(staff)
        changed = True
    if changed:
        db.session.commit()


# --- Storefront & Auth Routes ---

@app.route('/')
def index():
    view_mode = request.args.get('view')
    if current_user.is_authenticated and current_user.role == 'admin' and view_mode != 'store':
        return redirect(url_for('admin_analytics'))
    pizzas = Pizza.query.filter_by(is_available=True).all()
    return render_template('customer/menu.html', pizzas=pizzas)


@app.route('/boutique')
def boutique():
    pizzas = Pizza.query.filter_by(is_available=True).all()
    return render_template('customer/menu.html', pizzas=pizzas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_analytics'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff_dashboard'))
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Bienvenue, {user.username} !', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_analytics'))
            elif user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            return redirect(url_for('index'))
        flash('Identifiant ou mot de passe incorrect.', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('index'))


# --- Admin Routes ---

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Accès refusé", 403
    return redirect(url_for('admin_analytics'))


@app.route('/admin/menu', methods=['GET', 'POST'])
@login_required
def admin_menu():
    if current_user.role != 'admin':
        return "Accès refusé", 403
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        category = (request.form.get('category') or 'Pizza').strip()
        description = (request.form.get('description') or '').strip()
        try:
            price = float(request.form.get('price', 0))
        except (ValueError, TypeError):
            price = 0.0

        if not name or price <= 0:
            flash('Veuillez fournir un nom valide et un prix supérieur à 0 DH.', 'error')
            return redirect(url_for('admin_menu'))

        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_url = filename

        pizza = Pizza(
            name=name,
            category=category,
            description=description,
            photo_url=photo_url,
            base_price=price,
            is_available=True
        )
        db.session.add(pizza)
        db.session.commit()
        flash(f'L\'article "{name}" a été ajouté au menu.', 'success')
        return redirect(url_for('admin_menu'))

    pizzas = Pizza.query.all()
    toppings = Topping.query.all()
    return render_template('admin/menu.html', pizzas=pizzas, toppings=toppings)


@app.route('/admin/menu/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_menu(id):
    if current_user.role != 'admin':
        return "Accès refusé", 403
    pizza = db.get_or_404(Pizza, id)
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        category = (request.form.get('category') or 'Pizza').strip()
        description = (request.form.get('description') or '').strip()
        try:
            price = float(request.form.get('price', pizza.base_price))
        except (ValueError, TypeError):
            price = pizza.base_price

        if name:
            pizza.name = name
        pizza.category = category
        pizza.description = description
        if price > 0:
            pizza.base_price = price

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pizza.photo_url = filename

        db.session.commit()
        flash(f'L\'article "{pizza.name}" a été mis à jour.', 'success')
        return redirect(url_for('admin_menu'))
    return render_template('admin/edit_menu.html', pizza=pizza)


@app.route('/admin/pizza/<int:id>/toggle_availability')
@login_required
def toggle_availability(id):
    if current_user.role != 'admin':
        return "Accès refusé", 403
    pizza = db.get_or_404(Pizza, id)
    pizza.is_available = not pizza.is_available
    db.session.commit()
    status_label = "activé" if pizza.is_available else "masqué"
    flash(f'Article "{pizza.name}" {status_label}.', 'info')
    return redirect(url_for('admin_menu'))


@app.route('/admin/pizza/<int:id>/delete', methods=['POST'])
@login_required
def delete_pizza(id):
    if current_user.role != 'admin':
        return "Accès refusé", 403
    pizza = db.get_or_404(Pizza, id)
    name = pizza.name
    if pizza.order_items:
        pizza.is_available = False
        db.session.commit()
        flash(f'"{name}" est lié à des commandes existantes et a été archivé (masqué du menu).', 'warning')
    else:
        db.session.delete(pizza)
        db.session.commit()
        flash(f'L\'article "{name}" a été supprimé définitivement.', 'success')
    return redirect(url_for('admin_menu'))


# --- Staff Routes ---

@app.route('/staff')
@login_required
def staff_dashboard():
    if current_user.role not in ['staff', 'admin']:
        return "Accès refusé", 403
    orders = Commande.query.order_by(Commande.created_at.desc()).all()
    return render_template('staff/dashboard.html', orders=orders)


@app.route('/staff/order/<int:id>/update_status', methods=['POST'])
@login_required
def update_order_status(id):
    if current_user.role not in ['staff', 'admin']:
        return jsonify({"error": "Accès refusé"}), 403
    order = db.get_or_404(Commande, id)
    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    if new_status not in VALID_ORDER_STATUSES:
        return jsonify({"error": "Statut invalide"}), 400
    order.status = new_status
    db.session.commit()
    return jsonify({"message": "Statut mis à jour", "status": order.status, "order_id": order.id})


@app.route('/api/staff/summary')
@login_required
def api_staff_summary():
    if current_user.role not in ['staff', 'admin']:
        return jsonify({"error": "Accès refusé"}), 403
    new_count = Commande.query.filter_by(status='New').count()
    confirmed_count = Commande.query.filter_by(status='Confirmed').count()
    preparing_count = Commande.query.filter_by(status='Preparing').count()
    latest_order = Commande.query.order_by(Commande.id.desc()).first()
    return jsonify({
        "new_count": new_count,
        "confirmed_count": confirmed_count,
        "preparing_count": preparing_count,
        "latest_order_id": latest_order.id if latest_order else 0
    })


# --- Customer Checkout & Order Tracking Routes ---

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        full_name = (request.form.get('full_name') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        address = (request.form.get('address') or '').strip()
        neighborhood = (request.form.get('neighborhood') or '').strip()
        order_type = request.form.get('order_type') or 'Delivery'
        payment_method = request.form.get('payment_method') or 'Cash'
        cart_data = request.form.get('cart_data') or '[]'

        if not full_name or not phone:
            flash('Veuillez renseigner votre nom complet et votre numéro de téléphone.', 'error')
            return redirect(url_for('checkout'))

        if order_type == 'Delivery' and not address:
            flash('Veuillez renseigner votre adresse de livraison.', 'error')
            return redirect(url_for('checkout'))

        try:
            raw_items = json.loads(cart_data)
            if not isinstance(raw_items, list) or len(raw_items) == 0:
                raise ValueError("Empty cart")
        except (ValueError, TypeError):
            flash('Votre panier est vide ou invalide.', 'error')
            return redirect(url_for('index'))

        validated_items = []
        subtotal = 0.0
        for item in raw_items:
            try:
                pizza_id = int(item.get('id'))
                qty = max(1, int(item.get('quantity', 1)))
            except (ValueError, TypeError, AttributeError):
                continue

            pizza_obj = db.session.get(Pizza, pizza_id)
            if pizza_obj:
                unit_price = float(pizza_obj.base_price)
                validated_items.append((pizza_obj, qty, unit_price))
                subtotal += unit_price * qty

        if not validated_items:
            flash('Aucun article valide trouvé dans votre panier.', 'error')
            return redirect(url_for('index'))

        delivery_fee = 0.0 if (subtotal >= 60 or order_type == 'Pickup') else 10.0
        total = subtotal + delivery_fee

        # 1. Create or Update User and Client
        user = User.query.filter_by(username=phone).first()
        if not user:
            user = User(username=phone, password_hash=generate_password_hash('guest'), role='customer')
            db.session.add(user)
            db.session.flush()
            client = Client(user_id=user.id, full_name=full_name, phone=phone, address=address)
            db.session.add(client)
        else:
            client = user.client_profile
            if not client:
                client = Client(user_id=user.id, full_name=full_name, phone=phone, address=address)
                db.session.add(client)
            else:
                client.full_name = full_name
                client.phone = phone
                if address:
                    client.address = address

        db.session.flush()

        # 2. Create Commande
        new_order = Commande(
            client_id=client.id,
            status='New',
            order_type=order_type,
            total_price=total
        )
        db.session.add(new_order)
        db.session.flush()

        # 3. Add Items
        for pizza_obj, qty, _ in validated_items:
            order_item = OrderItem(
                commande_id=new_order.id,
                pizza_id=pizza_obj.id,
                quantity=qty
            )
            db.session.add(order_item)

        # 4. Handle Payment
        payment = Paiement(commande_id=new_order.id, amount=total, method=payment_method)
        db.session.add(payment)
        db.session.flush()

        if payment_method == 'Cash':
            cash = Cash(paiement_id=payment.id, amount_received=total, change_given=0.0)
            db.session.add(cash)

        # 5. Delivery Info
        if order_type == 'Delivery':
            delivery = PizzaLivraison(
                commande_id=new_order.id,
                address=address,
                neighborhood=neighborhood or 'Standard',
                delivery_fee=delivery_fee
            )
            db.session.add(delivery)

        # 6. Generate Invoice Record (Facture)
        inv_num = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{new_order.id:04d}"
        facture = Facture(
            commande_id=new_order.id,
            invoice_number=inv_num,
            content_html=f"Facture {inv_num} - Client: {full_name} - Total: {total:.2f} DH"
        )
        db.session.add(facture)

        db.session.commit()
        flash('Votre commande a bien été enregistrée !', 'success')
        return redirect(url_for('order_success', order_id=new_order.id))

    return render_template('customer/checkout.html')


@app.route('/order_success/<int:order_id>')
def order_success(order_id):
    order = db.get_or_404(Commande, order_id)
    return render_template('customer/order_success.html', order=order)


@app.route('/api/order/<int:order_id>/status')
def api_order_status(order_id):
    order = db.get_or_404(Commande, order_id)
    status_labels = {
        'New': 'Reçue (En attente d\'appel)',
        'Confirmed': 'Confirmée',
        'Preparing': 'En préparation au four',
        'Done': 'Prête / En livraison',
        'Cancelled': 'Annulée'
    }
    return jsonify({
        'order_id': order.id,
        'status': order.status,
        'status_label': status_labels.get(order.status, order.status),
        'total_price': order.total_price
    })


# --- Admin Orders, Clients & Analytics ---

@app.route('/admin/orders')
@login_required
def admin_orders():
    if current_user.role != 'admin':
        return "Accès refusé", 403

    client_id = request.args.get('client_id', type=int)
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    query = Commande.query
    selected_client = None

    if client_id:
        selected_client = db.session.get(Client, client_id)
        query = query.filter_by(client_id=client_id)

    if status_filter and status_filter in VALID_ORDER_STATUSES:
        query = query.filter_by(status=status_filter)

    if search_query:
        query = query.join(Client).filter(
            or_(
                Client.full_name.ilike(f'%{search_query}%'),
                Client.phone.ilike(f'%{search_query}%'),
                Commande.id == (int(search_query) if search_query.isdigit() else -1)
            )
        )

    orders = query.order_by(Commande.created_at.desc()).all()
    return render_template(
        'admin/orders.html',
        orders=orders,
        selected_client=selected_client,
        status_filter=status_filter,
        search_query=search_query
    )


@app.route('/admin/clients')
@login_required
def admin_clients():
    if current_user.role != 'admin':
        return "Accès refusé", 403
    search_query = request.args.get('q', '').strip()
    query = Client.query
    if search_query:
        query = query.filter(
            or_(
                Client.full_name.ilike(f'%{search_query}%'),
                Client.phone.ilike(f'%{search_query}%'),
                Client.address.ilike(f'%{search_query}%')
            )
        )
    clients = query.order_by(Client.id.desc()).all()
    return render_template('admin/clients.html', clients=clients, search_query=search_query)


@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if current_user.role != 'admin':
        return "Accès refusé", 403

    today = date.today()

    # KPIs (exclude cancelled orders from revenue)
    total_revenue = db.session.query(func.sum(Commande.total_price)).filter(Commande.status != 'Cancelled').scalar() or 0.0
    total_orders = Commande.query.count()
    active_orders = Commande.query.filter(Commande.status.in_(['New', 'Confirmed', 'Preparing'])).count()
    valid_orders_count = Commande.query.filter(Commande.status != 'Cancelled').count()
    avg_order = total_revenue / valid_orders_count if valid_orders_count > 0 else 0.0

    # Today & Item Stats
    orders_today = Commande.query.filter(func.date(Commande.created_at) == str(today)).count()
    pizzas_sold = db.session.query(func.sum(OrderItem.quantity)).scalar() or 0
    new_clients = Client.query.count()

    # Recent Orders (Latest 6)
    recent_orders = Commande.query.order_by(Commande.created_at.desc()).limit(6).all()

    # Best Sellers (Top 5)
    best_sellers = db.session.query(
        Pizza.name,
        Pizza.category,
        Pizza.base_price,
        func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem).group_by(Pizza.id).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()

    # Daily Sales (Last 7 Days - zero-filled for smooth chart)
    seven_days_ago = datetime.utcnow() - timedelta(days=6)
    raw_daily_sales = db.session.query(
        func.date(Commande.created_at).label('date'),
        func.sum(Commande.total_price).label('revenue')
    ).filter(
        Commande.created_at >= seven_days_ago,
        Commande.status != 'Cancelled'
    ).group_by(func.date(Commande.created_at)).all()

    sales_by_date = {str(row.date): float(row.revenue or 0) for row in raw_daily_sales}
    daily_sales = []
    for i in range(6, -1, -1):
        d_str = str(today - timedelta(days=i))
        daily_sales.append({'date': d_str, 'revenue': round(sales_by_date.get(d_str, 0.0), 2)})

    # Status breakdown for doughnut chart
    status_counts = {
        status: Commande.query.filter_by(status=status).count()
        for status in VALID_ORDER_STATUSES
    }

    return render_template(
        'admin/analytics.html',
        total_revenue=total_revenue,
        total_orders=total_orders,
        active_orders=active_orders,
        avg_order=avg_order,
        orders_today=orders_today,
        pizzas_sold=pizzas_sold,
        new_clients=new_clients,
        recent_orders=recent_orders,
        best_sellers=best_sellers,
        daily_sales=daily_sales,
        status_counts=status_counts
    )


# --- CLI Commands for Init ---

@app.cli.command("init-db")
def init_db():
    ensure_default_users()
    print("Database initialized! Default accounts ready: admin (admin123) & staff (staff123).")


with app.app_context():
    ensure_default_users()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
