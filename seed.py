"""
seed.py — Données de démonstration idempotentes.
Usage : python seed.py
"""
from database import init_db, get_db
from services import create_order, create_reservation, create_menu_item


def seed():
    init_db()

    # Read all counts in one connection, close before writing
    conn = get_db()
    needs_menu   = conn.execute('SELECT COUNT(*) FROM menu_items').fetchone()[0]   == 0
    needs_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]       == 0
    needs_res    = conn.execute('SELECT COUNT(*) FROM reservations').fetchone()[0] == 0
    conn.close()

    # ── MENU ─────────────────────────────────────────────────────────────────
    if needs_menu:
        menu = [
            {'category':'Entrées',          'name':"Soupe à l'oignon gratinée", 'price':9,  'description':'Bouillon de bœuf, emmental gratiné, croûtons',            'featured':False,'position':1},
            {'category':'Entrées',          'name':'Salade César',              'price':12, 'description':'Romaine croquante, parmesan, anchois, croûtons maison',   'featured':False,'position':2},
            {'category':'Entrées',          'name':'Foie gras de canard',       'price':18, 'description':'Toast briochés, confiture de figues et porto',            'featured':True, 'position':3},
            {'category':'Entrées',          'name':'Bruschetta tomates',        'price':8,  'description':"Tomates fraîches, basilic, huile d'olive, ail",           'featured':False,'position':4},
            {'category':'Plats principaux', 'name':'Steak frites',              'price':26, 'description':'Entrecôte 250g, frites maison, beurre café de Paris',     'featured':True, 'position':1},
            {'category':'Plats principaux', 'name':'Poulet rôti fermier',       'price':22, 'description':'Jus de rôti, légumes de saison, pommes de terre',         'featured':False,'position':2},
            {'category':'Plats principaux', 'name':'Risotto aux champignons',   'price':24, 'description':'Champignons sauvages, parmesan, huile de truffe',         'featured':False,'position':3},
            {'category':'Plats principaux', 'name':'Pasta carbonara',           'price':19, 'description':'Guanciale, œuf fermier, parmesan, poivre noir',           'featured':False,'position':4},
            {'category':'Plats principaux', 'name':'Saumon grillé',             'price':23, 'description':'Sauce citron-câpres, riz pilaf, légumes vapeur',          'featured':False,'position':5},
            {'category':'Plats principaux', 'name':'Tajine végétarien',         'price':20, 'description':'Légumes du soleil, couscous, épices berbères',            'featured':False,'position':6},
            {'category':'Desserts',         'name':'Crème brûlée',              'price':9,  'description':'Vanille de Madagascar, caramel croustillant',             'featured':True, 'position':1},
            {'category':'Desserts',         'name':'Tiramisu maison',           'price':9,  'description':'Mascarpone, café serré, amaretto, cacao',                 'featured':False,'position':2},
            {'category':'Desserts',         'name':'Fondant au chocolat',       'price':10, 'description':'Cœur coulant Valrhona, glace vanille artisanale',         'featured':False,'position':3},
            {'category':'Desserts',         'name':'Île flottante',             'price':7,  'description':'Crème anglaise vanille, caramel, pralin',                 'featured':False,'position':4},
            {'category':'Boissons',         'name':'Vin rouge / blanc (verre)', 'price':6,  'description':'Sélection Côtes du Rhône, Bordeaux, Bourgogne',           'featured':False,'position':1},
            {'category':'Boissons',         'name':'Eau minérale',              'price':3,  'description':'Évian plate ou Perrier pétillante — 50cl',                'featured':False,'position':2},
            {'category':'Boissons',         'name':'Café / Expresso',           'price':2,  'description':'Sélection grand cru torréfié sur place',                  'featured':False,'position':3},
            {'category':'Boissons',         'name':'Jus de fruits frais',       'price':4,  'description':'Orange pressée, citron, pomme — du jour',                 'featured':False,'position':4},
        ]
        for item in menu:
            create_menu_item(item)
        print(f"   ✅ {len(menu)} plats insérés")
    else:
        print("   ℹ️  Menu déjà présent — skipped")

    # ── COMMANDES ────────────────────────────────────────────────────────────
    if needs_orders:
        orders = [
            {'customer_name':'Sophie Martin', 'items':'1 Steak frites, 1 Crème brûlée, 1 Vin rouge',        'delivery_type':'sur place','pickup_time':'12h30','phone':'+33 6 11 22 33 44','status':'confirmed'},
            {'customer_name':'Thomas Leroy',  'items':'2 Risotto aux champignons, 2 Tiramisu, 2 Eaux',       'delivery_type':'livraison','pickup_time':'19h45','phone':'+33 6 55 66 77 88','status':'pending'},
            {'customer_name':'Clara Dubois',  'items':"1 Soupe à l'oignon, 1 Poulet rôti, 1 Fondant choco", 'delivery_type':'sur place','pickup_time':'13h00','phone':'+33 6 99 00 11 22','status':'done'},
            {'customer_name':'Marc Fontaine', 'items':'1 Foie gras, 1 Saumon grillé, 1 Île flottante',       'delivery_type':'sur place','pickup_time':'20h00','phone':'+33 6 33 44 55 66','status':'pending'},
        ]
        for o in orders:
            create_order(o)
        print(f"   ✅ {len(orders)} commandes insérées")
    else:
        print("   ℹ️  Commandes déjà présentes — skipped")

    # ── RÉSERVATIONS ─────────────────────────────────────────────────────────
    if needs_res:
        reservations = [
            {'customer_name':'Famille Moreau',         'party_size':4,  'reservation_time':'Samedi 19 Oct — 20h00',   'phone':'+33 6 12 34 56 78','status':'confirmed'},
            {'customer_name':'Julie Petit',             'party_size':2,  'reservation_time':'Dimanche 20 Oct — 12h30', 'phone':'+33 6 87 65 43 21','status':'pending'},
            {'customer_name':'Groupe Entreprise Nexia', 'party_size':10, 'reservation_time':'Lundi 21 Oct — 19h30',   'phone':'+33 1 42 00 00 00','status':'pending'},
            {'customer_name':'Alain Bernard',           'party_size':3,  'reservation_time':'Mardi 22 Oct — 20h30',   'phone':'+33 6 55 00 11 22','status':'cancelled'},
        ]
        for r in reservations:
            create_reservation(r)
        print(f"   ✅ {len(reservations)} réservations insérées")
    else:
        print("   ℹ️  Réservations déjà présentes — skipped")

    print("\n   → http://localhost:5000        (site client)")
    print("   → http://localhost:5000/admin  (dashboard admin)")
    print("   → http://localhost:5000/qr     (QR code)")


if __name__ == '__main__':
    print("🌱 Seeding Restaurant OS V1…")
    seed()
    print("\n✅ Done.")
