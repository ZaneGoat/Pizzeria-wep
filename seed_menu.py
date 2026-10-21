from app import app, ensure_default_users
from models import db, Pizza


def seed_data():
    with app.app_context():
        ensure_default_users()

        menu_items = [
            # Top Offres
            ("Offre Spéciale 1", "Une pizza artisanale au choix + boisson fraîche à prix réduit", "Top Offre", 45.0, "top offres 1.webp"),
            ("Offre Spéciale 2", "Le duo gourmand parfait pour votre soirée entre amis", "Top Offre", 50.0, "top offres 2.webp"),
            ("Offre Spéciale 3", "La formule favorite des familles avec garniture généreuse", "Top Offre", 55.0, "top offres 3.webp"),
            ("Offre Spéciale 4", "L'offre méga gourmande à ne surtout pas rater", "Top Offre", 60.0, "top offres 4.webp"),

            # Pizzas Artisanales
            ("Hawaiienne", "Sauce tomate maison, mozzarella fondante, jambon de dinde fumé, ananas caramélisé", "Pizza", 65.0, "Hawaiienne.jpg"),
            ("La Pecheur", "Cocktail de fruits de mer frais, calamars, crevettes, mozzarella, persillade à l'ail", "Pizza", 85.0, "La Pecheur.jpg"),
            ("La Veggie", "Légumes du soleil grillés, poivrons, champignons frais, olives noires, origan", "Pizza", 65.0, "la veggie.jpg"),
            ("Legend Chicken BBQ", "Blanc de poulet mariné, sauce BBQ fumée, oignons rouges, poivrons croquants", "Pizza", 75.0, "legend chiken BBQ.jpg"),
            ("Chicken Legend Chipotle", "Poulet croustillant, sauce chipotle épicée, maïs doux, mozzarella filante", "Pizza", 80.0, "chiken lengend chiptle.jpg"),
            ("Pizza 1/2 Kilo de Fromage", "Alliance généreuse de 500g de fromages affinés pour les vrais amateurs", "Pizza", 90.0, "Pizza 1 2 kilo de fromage.jpg"),
            ("Margherita", "Sauce tomate San Marzano, double mozzarella fraîche, basilic & origan sauvage", "Pizza", 55.0, "Margherita.jpg"),
            ("Regina", "Sauce tomate, jambon de dinde, champignons de Paris frais, mozzarella", "Pizza", 65.0, "Regina.jpg"),
            ("4 Fromages", "Mozzarella, parmesan reggiano, chèvre crémeux, gorgonzola affiné", "Pizza", 75.0, "4 Fromages.jpg"),
            ("Thon", "Thon entier de qualité, câpres, olives noires, oignons rouges, mozzarella", "Pizza", 65.0, "Thon.jpg"),
            ("Kebab", "Viande kebab grillée à la broche, oignons, mozzarella, sauce blanche maison", "Pizza", 75.0, "Kebab.jpg"),
            ("Pizza Time Spéciale", "Signature de la maison : viande hachée épicée, œuf fermier, poivrons, double mozzarella", "Pizza", 85.0, "pizzatime_special.jpg"),
            ("TexMex", "Bœuf épicé façon Texas, maïs croquant, piments jalapeños, cheddar & mozzarella", "Pizza", 80.0, "TexMex.jpg"),
            ("Calzone", "Pizza soufflée pliée au four, garnie de jambon, champignons, jaune d'œuf et mozzarella", "Pizza", 75.0, "Calzone.jpg"),
            ("Orientale", "Merguez artisanales, poivrons grillés, olives de l'Atlas, mozzarella, origan", "Pizza", 85.0, "Orientale.jpg"),

            # Desserts
            ("Tiramisu", "Recette authentique italienne au mascarpone onctueux et café expresso", "Dessert", 25.0, "Tiramisu.jpg"),
            ("Mousse au Chocolat", "Mousse aérienne préparée maison au chocolat noir 70%", "Dessert", 25.0, "Mousse au Chocolat.jpg"),
            ("Panna Cotta", "Crème vanillée ultra-douce accompagnée de son coulis de fruits rouges", "Dessert", 25.0, "Panna Cotta.jpg"),
            ("Tarte au Citron", "Tartelette sablée au citron jaune frais et meringue dorée au chalumeau", "Dessert", 25.0, "Tarte au Citron.jpg"),
            ("Glace Vanille / Chocolat", "Deux boules artisanales au choix avec chantilly et éclats de gaufrette", "Dessert", 20.0, "Glace Vanille Chocolat.jpg"),

            # Boissons
            ("Coca-Cola", "Canette glacée 33cl", "Boisson", 10.0, "coca cola.jpg"),
            ("Pepsi", "Canette glacée 33cl", "Boisson", 10.0, "pepsi.jpg"),
            ("Sprite", "Canette glacée 33cl aux extraits naturels de citron-lime", "Boisson", 10.0, "sprite.jpg"),
            ("Eau Minérale", "Bouteille fraîche 50cl", "Boisson", 8.0, "eau miniral.jpg"),
            ("Jus d’Orange Frais", "Oranges pressées à la minute, 100% naturel sans sucre ajouté", "Boisson", 15.0, "jus orange.jpg"),
            ("Jus Citron", "Citronnade maison fraîche à la menthe", "Boisson", 15.0, "jus citron.jpg"),
            ("Fanta Orange", "Canette glacée 33cl", "Boisson", 10.0, None),
            ("Café Espresso", "Expresso italien pur Arabica fraîchement moulu", "Boisson", 12.0, None),
        ]

        added_count = 0
        updated_count = 0
        for name, desc, cat, price, photo in menu_items:
            existing = Pizza.query.filter_by(name=name).first()
            if existing:
                existing.description = desc
                existing.category = cat
                existing.base_price = price
                if photo:
                    existing.photo_url = photo
                existing.is_available = True
                updated_count += 1
            else:
                item = Pizza(
                    name=name,
                    description=desc,
                    category=cat,
                    base_price=price,
                    photo_url=photo,
                    is_available=True
                )
                db.session.add(item)
                added_count += 1

        db.session.commit()
        print(f"Menu seeded successfully! ({added_count} added, {updated_count} updated)")


if __name__ == "__main__":
    seed_data()
