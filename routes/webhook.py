from flask import Blueprint, request, jsonify
from services import create_order, create_reservation

webhook_bp = Blueprint('webhook', __name__)

# ── In-memory session store: { phone: { state, ...conversation_data } } ────────
sessions = {}

# ── States ─────────────────────────────────────────────────────────────────────
AWAITING_CHOICE = 'awaiting_choice'
ORDER_ITEMS     = 'order_items'
ORDER_TYPE      = 'order_type'
ORDER_NAME      = 'order_name'
ORDER_TIME      = 'order_time'
RES_NAME        = 'res_name'
RES_SIZE        = 'res_size'
RES_TIME        = 'res_time'

GREETING = (
    "Bonjour 👋 Bienvenue chez *La Belle Table* !\n\n"
    "Que souhaitez-vous faire ?\n"
    "1️⃣ Commander\n"
    "2️⃣ Réserver une table\n\n"
    "_Tapez 1 ou 2_"
)

RESET_KEYWORDS = {'bonjour', 'hello', 'hi', 'start', 'menu', 'aide', 'restart', 'reset'}


def handle_message(phone: str, message: str) -> str:
    msg = message.strip().lower()

    # Init or reset session
    if phone not in sessions or msg in RESET_KEYWORDS:
        sessions[phone] = {'state': AWAITING_CHOICE}
        return GREETING

    session = sessions[phone]
    state   = session['state']

    # ── MAIN MENU ──────────────────────────────────────────────────────────────
    if state == AWAITING_CHOICE:
        if '1' in msg or 'command' in msg or 'order' in msg or 'commander' in msg:
            session['state'] = ORDER_ITEMS
            return (
                "Super ! 🍽️\n\n"
                "Que souhaitez-vous commander ?\n"
                "_Décrivez votre commande librement_\n"
                "_(ex: 1 steak frites, 2 tiramisu, 1 eau)_"
            )
        elif '2' in msg or 'réserv' in msg or 'reserv' in msg or 'table' in msg:
            session['state'] = RES_NAME
            return "Parfait ! 📅\n\nQuel est votre *nom* pour la réservation ?"
        else:
            return "Je n'ai pas compris 😅\n\nTapez *1* pour commander ou *2* pour réserver une table."

    # ── ORDER FLOW ─────────────────────────────────────────────────────────────
    elif state == ORDER_ITEMS:
        session['items'] = message
        session['state'] = ORDER_TYPE
        return "🛵 *Livraison* ou *sur place* ?\n\nRépondez *L* ou *S*"

    elif state == ORDER_TYPE:
        if msg.startswith('l') or 'livraison' in msg or 'livrer' in msg or 'livré' in msg:
            session['delivery_type'] = 'livraison'
        else:
            session['delivery_type'] = 'sur place'
        session['state'] = ORDER_NAME
        return "Votre *nom* s'il vous plaît ?"

    elif state == ORDER_NAME:
        session['customer_name'] = message.strip().title()
        session['state'] = ORDER_TIME
        return "⏰ À quelle *heure* souhaitez-vous être servi(e) ?\n_(ex: 12h30, 19h00)_"

    elif state == ORDER_TIME:
        order_data = {
            'customer_name': session.get('customer_name', 'Anonyme'),
            'items':         session.get('items', ''),
            'delivery_type': session.get('delivery_type', 'sur place'),
            'pickup_time':   message.strip(),
            'phone':         phone,
            'status':        'pending',
        }
        create_order(order_data)
        sessions.pop(phone, None)
        return (
            f"✅ *Commande confirmée !*\n\n"
            f"👤 {order_data['customer_name']}\n"
            f"🍽️ {order_data['items']}\n"
            f"📍 {order_data['delivery_type'].capitalize()}\n"
            f"⏰ {order_data['pickup_time']}\n\n"
            f"Nous vous contacterons pour confirmer. Merci ! 🙏\n\n"
            f"_Tapez 'menu' pour recommencer_"
        )

    # ── RESERVATION FLOW ───────────────────────────────────────────────────────
    elif state == RES_NAME:
        session['customer_name'] = message.strip().title()
        session['state'] = RES_SIZE
        return "Combien de *personnes* serez-vous ?\n_(ex: 2, 4, 6)_"

    elif state == RES_SIZE:
        # Extract digits if present
        digits = ''.join(c for c in message if c.isdigit())
        session['party_size'] = int(digits) if digits else 2
        session['state'] = RES_TIME
        return "📅 *Date et heure* de la réservation ?\n_(ex: Samedi 20h00, Demain 12h30)_"

    elif state == RES_TIME:
        res_data = {
            'customer_name':    session.get('customer_name', 'Anonyme'),
            'party_size':       session.get('party_size', 2),
            'reservation_time': message.strip(),
            'phone':            phone,
            'status':           'pending',
        }
        create_reservation(res_data)
        sessions.pop(phone, None)
        return (
            f"✅ *Réservation enregistrée !*\n\n"
            f"👤 {res_data['customer_name']}\n"
            f"👥 {res_data['party_size']} personne(s)\n"
            f"📅 {res_data['reservation_time']}\n\n"
            f"Confirmation sous 30 minutes. À très bientôt ! 🥂\n\n"
            f"_Tapez 'menu' pour recommencer_"
        )

    # ── FALLBACK ───────────────────────────────────────────────────────────────
    sessions.pop(phone, None)
    return GREETING


# ── ENDPOINT ───────────────────────────────────────────────────────────────────
@webhook_bp.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Accepts both JSON (tests) and form-data (Twilio production).
    Twilio sends: From=whatsapp:+336...  Body=message
    """
    if request.is_json:
        data    = request.get_json(silent=True) or {}
        phone   = data.get('From', 'test_user')
        message = data.get('Body', '').strip()
    else:
        phone   = request.form.get('From', 'test_user')
        message = request.form.get('Body', '').strip()

    if not message:
        return jsonify({'error': 'Body (message) est requis'}), 400

    reply = handle_message(phone, message)
    return jsonify({'reply': reply})
