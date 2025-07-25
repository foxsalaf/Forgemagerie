from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration renforcée
DATABASE_URL = os.environ.get('DATABASE_URL')
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# CONNEXION BASE DE DONNÉES AMÉLIORÉE
# =====================================================

def get_db_connection():
    """Connexion adaptative SQLite ou PostgreSQL avec gestion d'erreurs"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        logger.info(f"🔍 DATABASE_URL configuré: {bool(database_url)}")
        
        if database_url and 'postgresql' in database_url:
            # PostgreSQL (Railway)
            import psycopg2
            from psycopg2.extras import RealDictCursor
            # Fix pour URL PostgreSQL
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            logger.info("✅ Connexion PostgreSQL établie")
            return conn, 'postgresql'
        else:
            # SQLite pour développement local
            import sqlite3
            conn = sqlite3.connect('bagages.db', timeout=30.0)
            conn.row_factory = sqlite3.Row
            logger.info("✅ Connexion SQLite établie")
            return conn, 'sqlite'
    except Exception as e:
        logger.error(f"❌ Erreur connexion DB: {e}")
        raise

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """Exécute une requête avec gestion d'erreurs centralisée"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        logger.error(f"❌ Erreur requête DB: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

# =====================================================
# SERVICES MÉTIER
# =====================================================

def calculate_price(client_type, destination, pickup_address, bag_count):
    """Calcule le prix basé sur les vrais tarifs 2AV-Bagages."""
    # Tarifs de base par bagage selon le type de client
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
        if isinstance(bag_count, str) and bag_count.endswith('+'):
            num_bags = int(bag_count[:-1])
        else:
            num_bags = int(bag_count)
    except Exception:
        num_bags = 1
    
    # Calcul du prix total = base * nombre de bagages + supplément destination
    total_price = (price_per_bag * num_bags) + destination_supplements.get(destination, 10)
    return round(total_price, 2)

def send_email_notification(to_email, subject, booking_details):
    """Envoie un email de confirmation de réservation au client."""
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
            
            # Envoi de l'email via SMTP
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
            
            logger.info(f"✅ Email envoyé à {to_email}")
            return True
        else:
            logger.info(f"📧 [DEV] Email simulé pour {to_email}: {subject}")
            return True
    except Exception as e:
        logger.error(f"❌ Erreur envoi email: {e}")
        return False

# =====================================================
# DÉCORATEURS ET MIDDLEWARES
# =====================================================

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_booking_data(data):
    """Valide les données de réservation"""
    required_fields = ['client_type', 'destination', 'pickup_address', 
                      'pickup_datetime', 'client_name', 'client_email', 'client_phone']
    
    errors = []
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Le champ {field} est obligatoire")
    
    # Validation spécifique
    if data.get('client_type') not in ['individuel', 'famille', 'pmr']:
        errors.append("Type de client invalide")
    
    if data.get('destination') not in ['aeroport', 'gare', 'port', 'domicile']:
        errors.append("Destination invalide")
    
    # Validation de l'email
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if data.get('client_email') and not re.match(email_pattern, data['client_email']):
        errors.append("Format d'email invalide")
    
    return errors

# =====================================================
# ROUTES PRINCIPALES
# =====================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    """Traite une nouvelle réservation avec validation complète"""
    try:
        data = request.get_json()
        logger.info(f"📦 Nouvelle réservation reçue: {data.get('client_email', 'email_manquant')}")
        
        # Validation des données
        validation_errors = validate_booking_data(data)
        if validation_errors:
            return jsonify({
                'success': False, 
                'message': 'Données invalides',
                'errors': validation_errors
            }), 400
        
        # Calcul du prix
        estimated_price = calculate_price(
            data['client_type'],
            data['destination'],
            data['pickup_address'],
            data.get('bag_count', '1')
        )
        
        # Sauvegarde en base
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        try:
            if db_type == 'postgresql':
                cursor.execute('''
                    INSERT INTO bookings (
                        client_type, destination, pickup_address, pickup_datetime,
                        bag_count, client_name, client_email, client_phone,
                        special_instructions, estimated_price
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    data['client_type'], data['destination'], data['pickup_address'],
                    data['pickup_datetime'], data.get('bag_count', '1'),
                    data['client_name'], data['client_email'], data['client_phone'],
                    data.get('special_instructions', ''), estimated_price
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
                    data['client_type'], data['destination'], data['pickup_address'],
                    data['pickup_datetime'], data.get('bag_count', '1'),
                    data['client_name'], data['client_email'], data['client_phone'],
                    data.get('special_instructions', ''), estimated_price
                ))
                booking_id = cursor.lastrowid
            
            conn.commit()
            logger.info(f"✅ Réservation #{booking_id} créée avec succès")
            
            # Envoi de l'email de confirmation
            booking_info = data.copy()
            booking_info.update({
                'booking_id': booking_id,
                'estimated_price': estimated_price
            })
            
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
            conn.rollback()
            logger.error(f"Erreur sauvegarde réservation: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Erreur lors de la réservation: {e}")
        return jsonify({
            'success': False, 
            'message': f"Erreur lors de la réservation: {str(e)}"
        }), 500

@app.route('/calculate-price', methods=['POST'])
def calculate_price_route():
    """Calcule le prix en temps réel"""
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
        logger.error(f"Erreur calcul prix: {e}")
        return jsonify({'error': str(e)}), 500

# =====================================================
# ROUTES D'ADMINISTRATION
# =====================================================

@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    """Authentification admin avec base de données"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        logger.info(f"🔐 Tentative de connexion admin: {username}")
        
        # Vérification dans la base de données
        admin_user = execute_query(
            "SELECT * FROM admin_users WHERE username = %s AND is_active = true",
            (username,),
            fetch_one=True
        )
        
        if admin_user:
            logger.info(f"👤 Admin trouvé: {admin_user['username']}")
            
            if check_password_hash(admin_user['password_hash'], password):
                session['admin_logged_in'] = True
                session['admin_id'] = admin_user['id']
                session['admin_username'] = admin_user['username']
                session['admin_role'] = admin_user['role']
                
                # Mise à jour du last_login
                execute_query(
                    "UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    (admin_user['id'],),
                    fetch_all=False
                )
                
                logger.info(f"✅ Connexion admin réussie: {username}")
                return redirect(url_for('admin_dashboard'))
            else:
                logger.warning(f"❌ Mot de passe incorrect pour: {username}")
                flash('Identifiants incorrects', 'error')
        else:
            logger.warning(f"❌ Admin non trouvé: {username}")
            flash('Identifiants incorrects', 'error')
            
        return redirect(url_for('admin_login'))
            
    except Exception as e:
        logger.error(f"❌ Erreur authentification admin: {e}")
        flash('Erreur de connexion', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion admin avec audit"""
    admin_id = session.get('admin_id')
    if admin_id:
        logger.info(f"🚪 Déconnexion admin: {session.get('admin_username')}")
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Dashboard admin avec statistiques"""
    try:
        # Statistiques globales
        total_bookings = execute_query(
            "SELECT COUNT(*) as count FROM bookings",
            fetch_one=True
        )['count']
        
        pending_bookings = execute_query(
            "SELECT COUNT(*) as count FROM bookings WHERE status = 'pending'",
            fetch_one=True
        )['count']
        
        total_revenue = execute_query(
            "SELECT COALESCE(SUM(estimated_price), 0) as revenue FROM bookings WHERE status = 'completed'",
            fetch_one=True
        )['revenue']
        
        # Réservations récentes
        recent_bookings = execute_query(
            "SELECT * FROM bookings ORDER BY created_at DESC LIMIT 10"
        )
        
        return render_template('admin_dashboard.html',
                             total_bookings=total_bookings,
                             pending_bookings=pending_bookings,
                             total_revenue=float(total_revenue or 0),
                             recent_bookings=recent_bookings)
                             
    except Exception as e:
        logger.error(f"Erreur dashboard: {e}")
        flash('Erreur lors du chargement du dashboard', 'error')
        return render_template('admin_dashboard.html',
                             total_bookings=0, pending_bookings=0, 
                             total_revenue=0, recent_bookings=[])

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    """Liste des réservations avec filtrage"""
    try:
        status_filter = request.args.get('status', 'all')
        
        if status_filter == 'all':
            bookings = execute_query(
                "SELECT * FROM bookings ORDER BY created_at DESC"
            )
        else:
            bookings = execute_query(
                "SELECT * FROM bookings WHERE status = %s ORDER BY created_at DESC",
                (status_filter,)
            )
        
        return render_template('admin_bookings.html', 
                             bookings=bookings, 
                             status_filter=status_filter)
                             
    except Exception as e:
        logger.error(f"Erreur liste réservations: {e}")
        flash('Erreur lors du chargement des réservations', 'error')
        return render_template('admin_bookings.html', 
                             bookings=[], status_filter='all')

@app.route('/admin/update-status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    """Met à jour le statut d'une réservation avec audit"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
            return jsonify({'success': False, 'message': 'Statut invalide'}), 400
        
        # Récupération de l'ancien statut pour l'audit
        old_booking = execute_query(
            "SELECT * FROM bookings WHERE id = %s",
            (booking_id,),
            fetch_one=True
        )
        
        if not old_booking:
            return jsonify({'success': False, 'message': 'Réservation non trouvée'}), 404
        
        # Mise à jour du statut
        execute_query(
            "UPDATE bookings SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_status, booking_id),
            fetch_all=False
        )
        
        logger.info(f"✅ Statut réservation #{booking_id} mis à jour: {old_booking['status']} -> {new_status}")
        
        return jsonify({
            'success': True,
            'message': f'Statut mis à jour vers {new_status}',
            'booking_id': booking_id,
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Erreur mise à jour statut: {e}")
        return jsonify({'success': False, 'message': f"Erreur: {str(e)}"}), 500

# =====================================================
# ROUTES DE TEST ET SANTÉ
# =====================================================

@app.route('/health')
def health_check():
    """Check de santé de l'application"""
    try:
        # Test de connexion DB
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': db_type,
            'timestamp': '2024-01-01T00:00:00Z'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': '2024-01-01T00:00:00Z'
        }), 500

@app.route('/test')
def test():
    """Page de test pour vérifier le bon fonctionnement"""
    try:
        # Test de connexion et statistiques
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM bookings")
        count = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        
        return f"""
        <h1>🎉 2AV-Bagages - Test Complet</h1>
        <h2>✅ Statut de l'application</h2>
        <ul>
            <li><strong>Flask:</strong> ✅ Opérationnel</li>
            <li><strong>Base de données:</strong> ✅ {db_type.upper()} connectée</li>
            <li><strong>Réservations:</strong> {count}</li>
        </ul>
        
        <h2>🔗 Navigation</h2>
        <ul>
            <li><a href="/">🏠 Accueil</a></li>
            <li><a href="/admin/login">🔐 Administration</a></li>
            <li><a href="/health">💊 Health Check</a></li>
        </ul>
        """
    except Exception as e:
        logger.error(f"Erreur page test: {e}")
        return f"""
        <h1>⚠️ Test 2AV-Bagages</h1>
        <p>✅ Flask fonctionne</p>
        <p>❌ Problème: {e}</p>
        <p><a href="/">← Retour à l'accueil</a></p>
        """

# =====================================================
# GESTION D'ERREURS
# =====================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html') if os.path.exists('templates/errors/404.html') else """
    <h1>404 - Page non trouvée</h1>
    <p><a href="/">Retour à l'accueil</a></p>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur 500: {error}")
    return render_template('errors/500.html') if os.path.exists('templates/errors/500.html') else """
    <h1>500 - Erreur serveur</h1>
    <p>Une erreur s'est produite.</p>
    <p><a href="/">Retour à l'accueil</a></p>
    """, 500

# =====================================================
# INITIALISATION DE L'APPLICATION
# =====================================================

def init_app():
    """Initialise l'application et vérifie la base de données"""
    try:
        # Test de connexion
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Vérification de l'existence de la table bookings
        if db_type == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'bookings'
                )
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='bookings'
            """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists or (db_type == 'postgresql' and not table_exists[0]):
            logger.warning("Table bookings non trouvée - création nécessaire")
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Application initialisée - DB: {db_type}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        return False

# =====================================================
# LANCEMENT DE L'APPLICATION
# =====================================================

if __name__ == '__main__':
    logger.info("🚀 Démarrage 2AV-Bagages...")
    logger.info(f"🗄️ Base de données: {DATABASE_URL or 'SQLite local'}")
    
    # Initialisation de l'application
    if init_app():
        logger.info("✅ Initialisation réussie")
    else:
        logger.warning("⚠️ Problème d'initialisation - l'app continue")
    
    # Configuration du serveur
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🌐 Serveur démarré sur le port {port} (debug={debug_mode})")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
    
