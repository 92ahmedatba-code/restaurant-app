# 🍽️ Restaurant OS V1

MVP SaaS prêt à vendre pour restaurants.
**Menu en ligne · Commandes WhatsApp · Réservations · Dashboard Admin · QR Code**

---

## ⚡ Démarrage en 3 minutes

```bash
# 1. Installer Flask (seule dépendance)
pip install -r requirements.txt

# 2. Peupler la base avec des données de démo
python seed.py

# 3. Lancer le serveur
python app.py
```

| URL | Description |
|-----|-------------|
| `http://localhost:5000` | Site client — menu + réservations |
| `http://localhost:5000/admin` | Dashboard admin |
| `http://localhost:5000/qr` | Générateur QR code |

---

## 📁 Structure

```
restaurant-os/
│
├── app.py               ← Point d'entrée Flask + gestionnaires d'erreurs
├── database.py          ← SQLite init (WAL mode, migration auto)
├── services.py          ← Toute la logique métier (CRUD + stats)
├── seed.py              ← Données démo idempotentes
├── config.json          ← ⭐ Personnalisation restaurant (éditer ici)
├── requirements.txt     ← flask + gunicorn
├── Procfile             ← Déploiement Render / Railway
│
├── routes/
│   ├── orders.py        ← GET/POST /orders, PATCH /orders/<id>/status
│   ├── reservations.py  ← GET/POST /reservations, PATCH statut
│   ├── menu.py          ← CRUD /menu, upload image, reorder
│   ├── stats.py         ← GET /stats
│   ├── config_route.py  ← GET/POST /config
│   ├── webhook.py       ← POST /webhook/whatsapp (bot état)
│   └── pages.py         ← /, /admin, /qr
│
├── templates/
│   ├── index.html       ← Site client dynamique
│   ├── admin.html       ← Dashboard (commandes, résa, menu, settings)
│   └── qr.html          ← Générateur QR code (menu ou WhatsApp)
│
└── static/
    ├── css/main.css     ← Styles complets, mobile-first
    └── uploads/         ← Images des plats (créé automatiquement)
```

---

## 🎨 Personnaliser pour un restaurant

**Tout se passe dans `config.json`** (ou depuis l'onglet ⚙️ Settings du dashboard) :

```json
{
  "restaurant_name":  "Le Nouveau Bistro",
  "tagline":          "Cuisine Italienne · Lyon",
  "logo_emoji":       "🍕",
  "whatsapp_number":  "33612345678",
  "address":          "5 Place Bellecour, Lyon 2e",
  "phone":            "+33 4 72 00 00 00",
  "hours_lunch":      "Midi 12h–14h",
  "hours_dinner":     "Soir 19h30–22h",
  "colors": {
    "primary":        "#E63946",
    "primary_light":  "#FF6B6B"
  }
}
```

Le site se met à jour au prochain rechargement, sans redémarrer le serveur.

---

## 📡 API REST

### Commandes

```
GET    /orders                    → liste toutes les commandes
POST   /orders                    → créer une commande
PATCH  /orders/<id>/status        → changer statut (pending/confirmed/done)
```

**POST /orders**
```json
{ "customer_name": "Jean", "items": "1 steak frites", "delivery_type": "livraison", "pickup_time": "19h30", "phone": "+336..." }
```

### Réservations

```
GET    /reservations              → liste
POST   /reservations              → créer
PATCH  /reservations/<id>/status  → pending / confirmed / cancelled
```

### Menu

```
GET    /menu                      → plats disponibles (site public)
GET    /menu?all=1                → tous les plats (admin)
POST   /menu                      → ajouter un plat
PATCH  /menu/<id>                 → modifier (partiel — seuls les champs envoyés)
DELETE /menu/<id>                 → supprimer
POST   /menu/<id>/image           → upload photo (multipart/form-data, champ: image)
POST   /menu/reorder              → { "ids": [3,1,2] } — réordonner
```

### Stats

```
GET    /stats
→ { today_orders, today_reservations, pending_orders, done_today, total_orders, total_reservations }
```

### Config

```
GET    /config     → lire config.json
POST   /config     → mettre à jour config.json
```

### WhatsApp Webhook

```
POST   /webhook/whatsapp
Body:  { "From": "+33600000000", "Body": "Bonjour" }
→     { "reply": "Bonjour 👋 ..." }
```

**Test rapide :**
```bash
curl -X POST http://localhost:5000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"From": "+336xxx", "Body": "Bonjour"}'
```

---

## 💬 Connecter le vrai WhatsApp

1. Créer un compte [Twilio](https://console.twilio.com) (gratuit)
2. Exposer le serveur : `ngrok http 5000`
3. Dans Twilio → WhatsApp Sandbox → Webhook URL :
   ```
   https://xxxx.ngrok.io/webhook/whatsapp
   ```
4. Twilio envoie `From` et `Body` en form-data — **le webhook gère déjà les deux formats** (JSON + form-data).

---

## 🚀 Déploiement Render (gratuit)

### Prérequis
- Compte [Render](https://render.com)
- Repo Git (GitHub, GitLab)

### Étapes

```bash
# 1. Pousser le projet
git init && git add . && git commit -m "Restaurant OS V1"
git remote add origin https://github.com/vous/restaurant-os.git
git push -u origin main
```

2. Sur Render → **New Web Service** → connecter le repo
3. Paramètres :
   - **Runtime** : Python 3
   - **Build command** : `pip install -r requirements.txt`
   - **Start command** : `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
4. Variables d'environnement :
   - `SECRET_KEY` → une chaîne aléatoire sécurisée
   - `FLASK_ENV` → `production`
5. Cliquer **Deploy** → URL publique fournie automatiquement

> ⚠️ **Note SQLite en prod :** Render recrée le filesystem à chaque déploiement.
> Pour persister les données, utilisez un **Persistent Disk** Render ($7/mois)
> ou migrez vers PostgreSQL avec SQLAlchemy (changement minimal dans `database.py`).

### Déploiement Railway

```bash
# Installer Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

---

## 🔒 Sécurisation pour production

```python
# Dans app.py, remplacer :
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key')

# Ajouter basic auth admin (optionnel) :
# from functools import wraps
# from flask import request, Response
# def require_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth or auth.password != os.environ.get('ADMIN_PASSWORD','admin'):
#             return Response('Auth required', 401, {'WWW-Authenticate':'Basic realm="Admin"'})
#         return f(*args, **kwargs)
#     return decorated
```

---

## 🛠️ Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.9+ · Flask 3 |
| Base de données | SQLite (WAL mode) |
| Frontend | HTML5 · CSS3 · JS Vanilla |
| Upload images | Flask + filesystem local |
| QR Code | qrcode.js (CDN JS) |
| Chatbot WhatsApp | Machine à états (mots-clés) |
| Prod server | Gunicorn |

---

## 📋 Checklist avant démo client

- [ ] Remplir `config.json` avec les vraies infos du restaurant
- [ ] Lancer `python seed.py` pour les données de démo
- [ ] Vérifier le numéro WhatsApp dans config
- [ ] Ajouter les vrais plats depuis l'onglet 🍴 Menu
- [ ] Uploader quelques photos de plats
- [ ] Tester le bot depuis l'onglet 💬 WhatsApp du dashboard
- [ ] Imprimer le QR code depuis `/qr`

---

*Restaurant OS V1 — Simple. Stable. Vendable.*
