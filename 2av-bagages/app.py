from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from functools import wraps
from datetime import datetime, timedelta
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
        if DATABASE_URL and 'postgresql' in DATABASE_URL:
            # PostgreSQL (Railway)
            import psycopg2
            from psycopg2.extras import RealDictCursor
            # Fix pour URL PostgreSQL
            db_url = DATABASE_URL
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            return conn, 'postgresql'
        else:
            # SQLite pour développement local
            import sqlite3
            conn = sqlite3.connect('bagages.db', timeout=30.0)
            conn.row_factory = sqlite3.Row
            return conn, 'sqlite'
    except Exception as e:
        logger.error(f"Erreur connexion DB: {e}")
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
        logger.error(f"Erreur requête DB: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

# =====================================================
# SERVICES MÉTIER
# =====================================================

class PricingService:
    """Service de calcul des prix utilisant la base de données"""
    
    @staticmethod
    def calculate_price(client_type, destination, bag_count):
        """Calcule le prix en utilisant la fonction PostgreSQL ou les règles en dur"""
        try:
            conn, db_type = get_db_connection()
            cursor = conn.cursor()
            
            if db_type == 'postgresql':
                # Utilisation de la fonction PostgreSQL
                cursor.execute(
                    "SELECT calculate_booking_price(%s, %s, %s) as price",
                    (client_type, destination, bag_count)
                )
                result = cursor.fetchone()
                price = float(result['price']) if result else None
            else:
                # Fallback pour SQLite
                price = PricingService._calculate_price_fallback(client_type, destination, bag_count)
            
            cursor.close()
            conn.close()
            return price
            
        except Exception as e:
            logger.error(f"Erreur calcul prix: {e}")
            # Fallback en cas d'erreur
            return PricingService._calculate_price_fallback(client_type, destination, bag_count)
    
    @staticmethod
    def _calculate_price_fallback(client_type, destination, bag_count):
        """Calcul de prix de secours"""
        base_prices = {
            'pmr': 15.75,
            'famille': 13.75,
            'individuel': 17.00
        }
        
        destination_supplements = {
            'aeroport': 15.00,
            'gare': 8.00,
            'port': 12.00,
            'domicile': 5.00
        }
        
        price_per_bag = base_prices.get(client_type, 17.00)
        destination_supplement = destination_supplements.get(destination, 10.00)
        
        # Conversion du nombre de bagages
        try:
            if bag_count.endswith('+'):
                num_bags = int(bag_count[:-1])
            else:
                num_bags = int(bag_count)
        except:
            num_bags = 1
        
        return round((price_per_bag * num_bags) + destination_supplement, 2)

class SystemSettingsService:
    """Service de gestion des paramètres système"""
    
    @staticmethod
    def get_setting(key, default=None):
        """Récupère un paramètre système"""
        try:
            result = execute_query(
                "SELECT setting_value FROM system_settings WHERE setting_key = %s AND is_public = true",
                (key,),
                fetch_one=True
            )
            return result['setting_value'] if result else default
        except:
            return default
    
    @staticmethod
    def get_public_settings():
        """Récupère tous les paramètres publics"""
        try:
            results = execute_query(
                "SELECT setting_key, setting_value FROM system_settings WHERE is_public = true"
            )
            return {row['setting_key']: row['setting_value'] for row in results}
        except:
            return {}

class EmailService:
    """Service d'envoi d'emails avec templates"""
    
    @staticmethod
    def send_booking_confirmation(booking_data):
        """Envoie un email de confirmation de réservation"""
        try:
            # Récupération du template
            template = execute_query(
                "SELECT * FROM email_templates WHERE template_name = 'booking_confirmation' AND is_active = true",
                fetch_one=True
            )
            
            if not template:
                logger.warning("Template email non trouvé")
                return EmailService._send_fallback_email(booking_data)
            
            # Formatage du contenu
            content = template['html_content'].format(**booking_data)
            subject = template['subject'].format(**booking_data)
            
            return EmailService._send_email(booking_data['client_email'], subject, content)
            
        except Exception as e:
            logger.error(f"Erreur envoi email template: {e}")
            return EmailService._send_fallback_email(booking_data)
    
    @staticmethod
    def _send_fallback_email(booking_data):
        """Email de secours sans template"""
        try:
            if EMAIL_USER and EMAIL_PASS:
                import smtplib
                from email.mime.text import MIMEText
                
                content = f"""
                Bonjour {booking_data.get('client_name', '')},
                
                Votre réservation #{booking_data.get('booking_id', 'XXX')} a été confirmée.
                
                Détails :
                - Date : {booking_data.get('pickup_datetime', '')}
                - Adresse : {booking_data.get('pickup_address', '')}
                - Destination : {booking_data.get('destination', '')}
                - Bagages : {booking_data.get('bag_count', '')}
                - Prix : {booking_data.get('estimated_price', '')}€
                
                Cordialement,
                L'équipe 2AV-Bagages
                """
                
                msg = MIMEText(content, 'plain')
                msg['Subject'] = f"Confirmation réservation 2AV-Bagages #{booking_data.get('booking_id', 'XXX')}"
                msg['From'] = EMAIL_USER
                msg['To'] = booking_data['client_email']
                
                smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
                smtp_server.starttls()
                smtp_server.login(EMAIL_USER, EMAIL_PASS)
                smtp_server.send_message(msg)
                smtp_server.quit()
                
                logger.info(f"Email de confirmation envoyé à {booking_data['client_email']}")
                return True
            else:
                logger.info(f"[DEV] Email de confirmation simulé pour {booking_data['client_email']}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    @staticmethod
    def _send_email(to_email, subject, content):
        """Méthode générique d'envoi d'email"""
        # Implémentation similaire à _send_fallback_email
        # avec le contenu HTML du template
        pass

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
    
    # Validation de la date
    try:
        pickup_dt = datetime.strptime(data.get('pickup_datetime', ''), '%Y-%m-%d %H:%M')
        min_advance = SystemSettingsService.get_setting('booking_advance_hours', '6')
        min_datetime = datetime.now() + timedelta(hours=int(min_advance))
        
        if pickup_dt < min_datetime:
            errors.append(f"La réservation doit être faite au moins {min_advance}h à l'avance")
    except:
        errors.append("Format de date/heure invalide")
    
    return errors

# =====================================================
# ROUTES PRINCIPALES
# =====================================================

@app.route('/')
def index():
    # Récupération des paramètres publics pour la page
    settings = SystemSettingsService.get_public_settings()
    return render_template('index.html', settings=settings)

@app.route('/book', methods=['POST'])
def book():
    """Traite une nouvelle réservation avec validation complète"""
    try:
        data = request.get_json()
        logger.info(f"Nouvelle réservation reçue: {data.get('client_email', 'email_manquant')}")
        
        # Validation des données
        validation_errors = validate_booking_data(data)
        if validation_errors:
            return jsonify({
                'success': False, 
                'message': 'Données invalides',
                'errors': validation_errors
            }), 400
        
        # Calcul du prix
        estimated_price = PricingService.calculate_price(
            data['client_type'],
            data['destination'],
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
            logger.info(f"Réservation #{booking_id} créée avec succès")
            
            # Envoi de l'email de confirmation
            booking_info = data.copy()
            booking_info.update({
                'booking_id': booking_id,
                'estimated_price': estimated_price
            })
            
            EmailService.send_booking_confirmation(booking_info)
            
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
        price = PricingService.calculate_price(
            data.get('client_type', 'individuel'),
            data.get('destination', 'aeroport'),
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
        # Vérification dans la base de données
        admin_user = execute_query(
            "SELECT * FROM admin_users WHERE username = %s AND is_active = true",
            (username,),
            fetch_one=True
        )
        
        if admin_user and check_password_hash(admin_user['password_hash'], password):
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
            
            logger.info(f"Connexion admin réussie: {username}")
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants incorrects', 'error')
            logger.warning(f"Tentative de connexion échouée: {username}")
            return redirect(url_for('admin_login'))
            
    except Exception as e:
        logger.error(f"Erreur authentification admin: {e}")
        flash('Erreur de connexion', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion admin avec audit"""
    admin_id = session.get('admin_id')
    if admin_id:
        try:
            # Log de déconnexion
            execute_query(
                "INSERT INTO audit_log (table_name, record_id, action, new_values, changed_by) VALUES (%s, %s, %s, %s, %s)",
                ('admin_users', admin_id, 'LOGOUT', '{"action": "logout"}', admin_id),
                fetch_all=False
            )
        except:
            pass  # Ne pas bloquer la déconnexion en cas d'erreur d'audit
    
    session.clear()
    logger.info("Déconnexion admin")
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Dashboard admin avec statistiques de la vue"""
    try:
        # Récupération des statistiques via la vue
        stats = execute_query(
            "SELECT * FROM v_dashboard_stats",
            fetch_one=True
        )
        
        # Réservations récentes
        recent_bookings = execute_query(
            "SELECT * FROM v_recent_bookings LIMIT 10"
        )
        
        return render_template('admin_dashboard.html',
                             total_bookings=stats['total_bookings'],
                             pending_bookings=stats['pending_bookings'],
                             total_revenue=float(stats['total_revenue'] or 0),
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
        
        # Audit log
        admin_id = session.get('admin_id')
        execute_query(
            "INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, changed_by) VALUES (%s, %s, %s, %s, %s, %s)",
            ('bookings', booking_id, 'UPDATE', 
             json.dumps({'status': old_booking['status']}),
             json.dumps({'status': new_status}),
             admin_id),
            fetch_all=False
        )
        
        # Envoi d'email de notification de changement de statut (optionnel)
        try:
            booking_info = {
                'booking_id': booking_id,
                'client_name': old_booking['client_name'],
                'client_email': old_booking['client_email'],
                'status': new_status
            }
            # EmailService.send_status_update(booking_info)  # À implémenter
        except:
            pass  # Ne pas bloquer si l'email échoue
        
        logger.info(f"Statut réservation #{booking_id} mis à jour: {old_booking['status']} -> {new_status}")
        
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
# ROUTES API POUR LES STATISTIQUES
# =====================================================

@app.route('/api/stats/daily')
@admin_required
def api_daily_stats():
    """API pour les statistiques quotidiennes"""
    try:
        target_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        stats = execute_query(
            "SELECT generate_daily_stats(%s) as stats",
            (target_date,),
            fetch_one=True
        )
        
        return jsonify(stats['stats'])
    except Exception as e:
        logger.error(f"Erreur stats quotidiennes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pricing/update', methods=['POST'])
@admin_required
def api_update_pricing():
    """API pour mettre à jour les tarifs"""
    try:
        data = request.get_json()
        admin_id = session.get('admin_id')
        
        # Validation des données
        required_fields = ['client_type', 'destination', 'base_price_per_bag', 'destination_supplement']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Champ {field} manquant'}), 400
        
        # Insertion de la nouvelle règle
        execute_query(
            """INSERT INTO pricing_rules 
               (client_type, destination, base_price_per_bag, destination_supplement, effective_date) 
               VALUES (%s, %s, %s, %s, CURRENT_DATE)""",
            (data['client_type'], data['destination'], 
             data['base_price_per_bag'], data['destination_supplement']),
            fetch_all=False
        )
        
        logger.info(f"Tarifs mis à jour par admin {admin_id}")
        return jsonify({'success': True, 'message': 'Tarifs mis à jour'})
        
    except Exception as e:
        logger.error(f"Erreur mise à jour tarifs: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# GESTION D'ERREURS
# =====================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur 500: {error}")
    return render_template('errors/500.html'), 500

# =====================================================
# ROUTE DE TEST ET SANTÉ
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
        
        # Test des paramètres système
        settings_count = len(SystemSettingsService.get_public_settings())
        
        return jsonify({
            'status': 'healthy',
            'database': db_type,
            'settings_loaded': settings_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test')
def test():
    """Page de test pour vérifier le bon fonctionnement"""
    try:
        # Test de connexion et statistiques
        stats = execute_query("SELECT * FROM v_dashboard_stats", fetch_one=True)
        settings = SystemSettingsService.get_public_settings()
        
        conn, db_type = get_db_connection()
        conn.close()
        
        return f"""
        <h1>🎉 2AV-Bagages - Test Complet</h1>
        <h2>✅ Statut de l'application</h2>
        <ul>
            <li><strong>Flask:</strong> ✅ Opérationnel</li>
            <li><strong>Base de données:</strong> ✅ {db_type.upper()} connectée</li>
            <li><strong>Réservations:</strong> {stats['total_bookings'] if stats else 0}</li>
            <li><strong>Configuration:</strong> {len(settings)} paramètres chargés</li>
        </ul>
        
        <h2>📊 Statistiques</h2>
        <ul>
            <li>Total réservations: {stats['total_bookings'] if stats else 0}</li>
            <li>En attente: {stats['pending_bookings'] if stats else 0}</li>
            <li>Terminées: {stats['completed_bookings'] if stats else 0}</li>
            <li>Chiffre d'affaires: {stats['total_revenue'] if stats else 0}€</li>
        </ul>
        
        <h2>🔗 Navigation</h2>
        <ul>
            <li><a href="/">🏠 Accueil</a></li>
            <li><a href="/admin/login">🔐 Administration</a></li>
            <li><a href="/health">💊 Health Check</a></li>
        </ul>
        
        <h2>⚙️ Configuration système</h2>
        <ul>
        {''.join([f"<li><strong>{k}:</strong> {v}</li>" for k, v in settings.items()])}
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
            # Ici vous pourriez exécuter le script de création automatiquement
        
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
    
    # Affichage des routes principales
    logger.info("📍 Routes disponibles:")
    logger.info("   🏠 / - Page d'accueil")
    logger.info("   🔐 /admin/login - Connexion admin")
    logger.info("   📊 /admin - Dashboard")
    logger.info("   📋 /admin/bookings - Gestion réservations")
    logger.info("   🧪 /test - Page de test")
    logger.info("   💊 /health - Health check")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
