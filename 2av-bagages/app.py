from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Utilisation d'un mot de passe admin haché pour plus de sécurité
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')
if not ADMIN_PASSWORD_HASH:
    # Générer un hash du mot de passe admin en clair s'il n'est pas déjà fourni haché
    ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

# Base de données - détection automatique SQLite/PostgreSQL
def get_db_connection():
    """Connexion adaptative SQLite ou PostgreSQL"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url and 'postgresql' in database_url:
        # PostgreSQL (ex: sur Railway)
        import psycopg2
        from psycopg2.extras import RealDictCursor
        # Fix pour URL PostgreSQL éventuellement mal formatée (postgres:// -> postgresql://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn, 'postgresql'
    else:
        # SQLite pour développement local (fichier bagages.db)
        import sqlite3
        conn = sqlite3.connect('bagages.db')
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        return conn, 'sqlite'

def init_db():
    """Initialise la base de données (SQLite ou PostgreSQL) et crée la table bookings si nécessaire."""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        print(f"🗄️ Initialisation base de données {db_type}")
        # Création de la table bookings si elle n'existe pas déjà
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
                    client_type VARCHAR(50) NOT NULL,
                    destination VARCHAR(50) NOT NULL,
                    pickup_address TEXT NOT NULL,
                    pickup_datetime VARCHAR(50) NOT NULL,
                    bag_count VARCHAR(10) NOT NULL,
                    client_name VARCHAR(100) NOT NULL,
                    client_email VARCHAR(100) NOT NULL,
                    client_phone VARCHAR(20) NOT NULL,
                    special_instructions TEXT,
                    estimated_price DECIMAL(10,2),
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_type TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    pickup_address TEXT NOT NULL,
                    pickup_datetime TEXT NOT NULL,
                    bag_count TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    client_email TEXT NOT NULL,
                    client_phone TEXT NOT NULL,
                    special_instructions TEXT,
                    estimated_price REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
        # Vérification de la connexion et du nombre de réservations initial
        cursor.execute("SELECT COUNT(*) AS count FROM bookings")
        result = cursor.fetchone()
        print(f"✅ Base de données {db_type} initialisée - {result['count'] if result else 0} réservations")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur init DB: {e}")
        print(f"🔍 Variables env.: DATABASE_URL={os.environ.get('DATABASE_URL', 'Non définie')}")

# Décorateur pour exiger l'authentification admin sur certaines routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Calculateur de prix avec les vrais tarifs 2AV-Bagages
def calculate_price(client_type, destination, pickup_address, bag_count):
    """Calcule le prix basé sur les vrais tarifs 2AV-Bagages."""
    # Tarifs de base par bagage selon le type de client (pour un nombre de bagages donné)
    base_prices = {
        'pmr': 15.75,      # 63€ pour 4 bagages (15.75€ par bagage)
        'famille': 13.75,  # 110€ pour 8 bagages (13.75€ par bagage)  
        'individuel': 17   # 68€ pour 4 bagages (17€ par bagage)
    }
    # Suppléments fixes selon la destination
    destination_supplements = {
        'aeroport': 15,
        'gare': 8,
        'port': 12,
        'domicile': 5
    }
    price_per_bag = base_prices.get(client_type, 17)
    # Nombre de bagages (conversion robuste de la valeur reçue)
    try:
        num_bags = int(bag_count)
    except Exception:
        if isinstance(bag_count, str) and bag_count.endswith('+'):
            # Si la valeur se termine par '+', on prend la partie numérique
            try:
                num_bags = int(bag_count[:-1])
            except Exception:
                num_bags = 1
        else:
            num_bags = 1
    # Calcul du prix total = base * nombre de bagages + supplément destination
    total_price = (price_per_bag * num_bags) + destination_supplements.get(destination, 10)
    return round(total_price, 2)

# Notification par email (confirmation de réservation)
def send_email_notification(to_email, subject, booking_details):
    """Envoie un email de confirmation de réservation au client (ou log en mode développement)."""
    try:
        if EMAIL_USER and EMAIL_PASS:
            # Composer le message de confirmation avec les détails de la réservation
            message_body = f"Bonjour {booking_details.get('client_name', '')},\n\n"
            message_body += f"Merci d'avoir réservé avec 2AV-Bagages. Voici les détails de votre réservation #{booking_details.get('booking_id')} :\n"
            message_body += f"- Destination : {booking_details.get('destination')}\n"
            message_body += f"- Adresse de prise en charge : {booking_details.get('pickup_address')}\n"
            message_body += f"- Date et heure de prise en charge : {booking_details.get('pickup_datetime')}\n"
            message_body += f"- Nombre de bagages : {booking_details.get('bag_count', '1')}\n"
            message_body += f"- Prix estimé : {booking_details.get('estimated_price', 'N/A')} €\n\n"
            message_body += "Nous vous contacterons si nécessaire pour plus de détails.\n"
            message_body += "Cordialement,\nL'équipe 2AV-Bagages"
            # Envoi de l'email via SMTP (configuration Gmail)
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(message_body, 'plain')
            msg['Subject'] = subject
            msg['From'] = EMAIL_USER
            msg['To'] = to_email
            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()
            smtp_server.login(EMAIL_USER, EMAIL_PASS)
            smtp_server.send_message(msg)
            smtp_server.quit()
            print(f"✅ Email envoyé à {to_email}")
            return True
        else:
            # En mode développement ou si aucune config email n'est fournie, on log l'email au lieu d'envoyer
            print(f"📧 [DEV] Email à envoyer : To: {to_email}, Subject: {subject}, Booking #{booking_details.get('booking_id')}")
            return True
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    """Traite une nouvelle réservation (endpoint appelé en AJAX par le formulaire client)."""
    try:
        data = request.get_json()
        print(f"📦 Nouvelle réservation reçue: {data}")
        # Validation des données requises
        if not data:
            return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
        required_fields = ['client_type', 'destination', 'pickup_address', 'pickup_datetime', 'client_name', 'client_email', 'client_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Champ {field} requis'}), 400
        # Calculer le prix estimé
        estimated_price = calculate_price(
            data['client_type'],
            data['destination'],
            data['pickup_address'],
            data.get('bag_count', '1')
        )
        # Sauvegarder la réservation en base de données
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        if db_type == 'postgresql':
            cursor.execute('''
                INSERT INTO bookings (
                    client_type, destination, pickup_address, pickup_datetime,
                    bag_count, client_name, client_email, client_phone,
                    special_instructions, estimated_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                data['client_type'],
                data['destination'],
                data['pickup_address'],
                data['pickup_datetime'],
                data.get('bag_count', '1'),
                data['client_name'],
                data['client_email'],
                data['client_phone'],
                data.get('special_instructions', ''),
                estimated_price
            ))
            booking_id = cursor.fetchone()[0]
        else:
            cursor.execute('''
                INSERT INTO bookings (
                    client_type, destination, pickup_address, pickup_datetime,
                    bag_count, client_name, client_email, client_phone,
                    special_instructions, estimated_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['client_type'],
                data['destination'],
                data['pickup_address'],
                data['pickup_datetime'],
                data.get('bag_count', '1'),
                data['client_name'],
                data['client_email'],
                data['client_phone'],
                data.get('special_instructions', ''),
                estimated_price
            ))
            booking_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Réservation #{booking_id} créée avec succès")
        # Envoi d'un email de confirmation au client
        booking_info = data.copy()
        booking_info['booking_id'] = booking_id
        send_email_notification(
            data['client_email'],
            f"Confirmation réservation 2AV-Bagages #{booking_id}",
            booking_info
        )
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'estimated_price': estimated_price,
            'message': 'Réservation confirmée avec succès !'
        })
    except Exception as e:
        print(f"❌ Erreur lors de la réservation: {e}")
        return jsonify({'success': False, 'message': f"Erreur lors de la réservation: {str(e)}"}), 500

@app.route('/calculate-price', methods=['POST'])
def calculate_price_route():
    """Calcule le prix en temps réel (appel AJAX pour afficher un tarif instantané)."""
    try:
        data = request.get_json()
        price = calculate_price(
            data.get('client_type', 'individuel'),
            data.get('destination', 'aeroport'),
            data.get('pickup_address', ''),
            data.get('bag_count', '1')
        )
        return jsonify({'price': price})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes d’administration
@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    """Authentification de l’admin avec vérification du mot de passe haché."""
    username = request.form.get('username')
    password = request.form.get('password')
    if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Identifiants incorrects', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion de l’admin."""
    session.clear()  # Nettoyer toute la session (équivalent à supprimer admin_logged_in)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Tableau de bord administrateur avec statistiques et réservations récentes."""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        # Statistiques globales
        cursor.execute('SELECT COUNT(*) AS total_bookings FROM bookings')
        total_bookings = cursor.fetchone()['total_bookings']
        cursor.execute("SELECT COUNT(*) AS pending_count FROM bookings WHERE status = 'pending'")
        pending_bookings = cursor.fetchone()['pending_count']
        cursor.execute("SELECT COALESCE(SUM(estimated_price), 0) AS revenue FROM bookings WHERE status = 'completed'")
        total_revenue = cursor.fetchone()['revenue']
        # Récupérer quelques dernières réservations
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC LIMIT 10')
        recent_bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin_dashboard.html',
                               total_bookings=total_bookings,
                               pending_bookings=pending_bookings,
                               total_revenue=float(total_revenue or 0),
                               recent_bookings=recent_bookings)
    except Exception as e:
        print(f"❌ Erreur dashboard: {e}")
        return f"Erreur: {e}", 500

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    """Liste filtrable des réservations complètes pour l'admin."""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        status_filter = request.args.get('status', 'all')
        if status_filter == 'all':
            cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        else:
            if db_type == 'postgresql':
                cursor.execute('SELECT * FROM bookings WHERE status = %s ORDER BY created_at DESC', (status_filter,))
            else:
                cursor.execute('SELECT * FROM bookings WHERE status = ? ORDER BY created_at DESC', (status_filter,))
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('admin_bookings.html', bookings=bookings, status_filter=status_filter)
    except Exception as e:
        print(f"❌ Erreur bookings: {e}")
        return f"Erreur: {e}", 500

# Route de test (vérification du bon fonctionnement)
@app.route('/test')
def test():
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM bookings")
        count = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        return f"""
        <h1>🎉 2AV-Bagages Test</h1>
        <p>✅ Flask fonctionne !</p>
        <p>✅ Base de données {db_type} connectée !</p>
        <p>📊 {count} réservations en base</p>
        <p><a href="/">← Retour à l'accueil</a></p>
        <p><a href="/admin/login">🔐 Admin</a></p>
        """
    except Exception as e:
        return f"""
        <h1>⚠️ Test 2AV-Bagages</h1>
        <p>✅ Flask fonctionne !</p>
        <p>❌ Problème base de données: {e}</p>
        <p><a href="/">← Retour à l'accueil</a></p>
        """

# Gestion des erreurs (pages 404 et 500 personnalisées)
@app.errorhandler(404)
def not_found(error):
    return """
    <h1>404 - Page non trouvée</h1>
    <p><a href="/">Retour à l'accueil</a></p>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    return """
    <h1>500 - Erreur serveur</h1>
    <p>Une erreur s'est produite.</p>
    <p><a href="/">Retour à l'accueil</a></p>
    """, 500

# Route API pour mettre à jour le statut d'une réservation (depuis le tableau de bord admin)
@app.route('/admin/update-status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    """Met à jour le statut d'une réservation existante (pending, confirmed, completed ou cancelled)."""
    try:
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
            return jsonify({'success': False, 'message': 'Statut invalide'}), 400
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        if db_type == 'postgresql':
            cursor.execute('''
                UPDATE bookings
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            ''', (new_status, booking_id))
        else:
            cursor.execute('''
                UPDATE bookings
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_status, booking_id))
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Réservation non trouvée'}), 404
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Statut mis à jour: Réservation #{booking_id} -> {new_status}")
        return jsonify({
            'success': True,
            'message': f'Statut mis à jour vers {new_status}',
            'booking_id': booking_id,
            'new_status': new_status
        })
    except Exception as e:
        print(f"❌ Erreur update statut: {e}")
        return jsonify({'success': False, 'message': f"Erreur lors de la mise à jour: {str(e)}"}), 500

# Lancement de l'application Flask
if __name__ == '__main__':
    print("🚀 Démarrage 2AV-Bagages...")
    print(f"🗄️ Base de données utilisée : {os.environ.get('DATABASE_URL', 'SQLite local')}")
    init_db()  # Initialiser la base de données au démarrage
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    print(f"🌐 Serveur démarré sur le port {port} (debug={debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
