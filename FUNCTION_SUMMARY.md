# Project Function & Architecture Summary

This document summarizes the Python backend routes, models, and frontend components of **Chef Amin Pizzeria (v2.0)**.

## Project File Structure

- `app.py` — Main Flask application, authentication, storefront, checkout, Kitchen KDS, Admin CRUD, and JSON API routes
- `models.py` — SQLAlchemy models (`User`, `Client`, `Pizza`, `Topping`, `Commande`, `OrderItem`, `Paiement`, `Cash`, `PizzaLivraison`, `Facture`)
- `install.sh` — Automated setup script (virtual environment, dependencies, DB initialization, menu & sample seeding)
- `requirements.txt` — Python package dependencies (compatible with Python 3.10–3.14+)
- `seed_menu.py` — Idempotent menu seeder (preserves foreign keys on existing orders)
- `seed_samples.py` — Realistic Moroccan customer & order generator
- `static/`
  - `css/style.css` — Dark-glass culinary design system & responsive layouts
  - `js/main.js` — Global cart badge synchronization, toast notifications, mobile nav & Web Audio KDS chime
  - `img/` — Product photography & brand assets
- `templates/`
  - `base.html` — Master layout, sticky glass navigation, flash messages & floating cart
  - `login.html` — Staff & Admin authentication page
  - `customer/` — `menu.html`, `checkout.html`, `order_success.html`
  - `staff/` — `dashboard.html` (Kitchen Display System)
  - `admin/` — `analytics.html`, `orders.html`, `clients.html`, `menu.html`, `edit_menu.html`, `dashboard.html`

## Core Routes (`app.py`)

| Route | Methods | Access | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Public | Customer storefront (redirects Admin to `/admin/analytics` unless `?view=store`) |
| `/boutique` | `GET` | Public | Direct link to customer storefront for all roles |
| `/login` | `GET, POST` | Public | Authenticates `admin` and `staff` accounts |
| `/logout` | `GET` | Authenticated | Logs out the current user |
| `/checkout` | `GET, POST` | Public | Validates cart items server-side, creates `Client`, `Commande`, `OrderItem`, `Paiement`, `PizzaLivraison`, and `Facture` |
| `/order_success/<id>` | `GET` | Public | Displays 4-step live order tracker and printable receipt |
| `/api/order/<id>/status` | `GET` | Public | JSON endpoint returning live order status for customer polling |
| `/staff` | `GET` | Staff / Admin | 3-column Kitchen Display System (KDS) with itemized cards |
| `/staff/order/<id>/update_status` | `POST` | Staff / Admin | Updates order status (`New`, `Confirmed`, `Preparing`, `Done`, `Cancelled`) |
| `/api/staff/summary` | `GET` | Staff / Admin | JSON endpoint for KDS auto-refresh & new order chime detection |
| `/admin/analytics` | `GET` | Admin | KPI dashboard, 7-day Chart.js sales evolution, Top 5 best sellers & recent orders |
| `/admin/orders` | `GET` | Admin | Searchable order manager with `?client_id=` and `?q=` filtering |
| `/admin/clients` | `GET` | Admin | Searchable CRM directory with lifetime spend and order count |
| `/admin/menu` | `GET, POST` | Admin | Menu inventory table and new item creation with image upload |
| `/admin/menu/edit/<id>` | `GET, POST` | Admin | Edit existing menu item details and photo |
| `/admin/pizza/<id>/toggle_availability` | `GET` | Admin | Toggle item visibility on the customer storefront |
| `/admin/pizza/<id>/delete` | `POST` | Admin | Safely deletes unreferenced items or archives items linked to past orders |
