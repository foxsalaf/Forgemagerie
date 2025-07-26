#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2AV-Bagages - Plateforme de transport de bagages PACA
Application Flask moderne avec interface glassmorphism
"""

import os
import sqlite3
import hashlib
import secrets
import re
import logging
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, jsonify, flash, g
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import bcrypt

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration de l'application
app = Flask(__name__)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    logger.warning("SECRET_KEY non définie, génération d'une clé temporaire")
    secret_key = secrets.token_hex(32)
app.secret_key = secret_key

# Configuration
DATABASE = 'bagages.db'
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')

# Hachage sécurisé du mot de passe admin
admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
if admin_password == 'admin123':
    logger.warning("Mot de passe admin par défaut détecté! Changez ADMIN_PASSWORD dans les variables d'environnement")
ADMIN_PASSWORD_HASH = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Configuration email
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Tarification de base
BASE_PRICING = {
    'pmr': {
        'aeroport': {'base': 15.75, 'supplement': 15.00},
        'gare': {'base': 15.75, 'supplement': 8.00},
        'port': {'base': 15.75, 'supplement': 12.00},
        'domicile': {'base': 15.75, 'supplement': 5.00}
    },
    'famille': {
        'aeroport': {'base': 13.75, 'supplement': 15.00},
        'gare': {'base': 13.75, 'supplement': 8.00},
        'port': {'base': 13.75, 'supplement': 12.00},
        'domicile': {'base': 13.75, 'supplement': 5.00}
    },
    'individuel': {
        'aeroport': {'base': 17.00, 'supplement': 15.00},
        'gare': {'base': 17.00, 'supplement': 8.00},
        'port': {'base': 17.00, 'supplement': 12.00},
        'domicile': {'base': 17.00, 'supplement': 5.00}
    }
}

@contextmanager
def get_db_connection():
    """Connexion à la base de données avec gestion automatique"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur base de données: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """Initialisation de la base de données avec gestion d'erreur"""
    try:
        with get_db_connection() as conn:
            # Adapter la requête pour PostgreSQL ou SQLite
            database_url = os.environ.get('DATABASE_URL', '')
            
            if 'postgresql' in database_url:
                # PostgreSQL
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bookings (
                        id SERIAL PRIMARY KEY,
                        client_type VARCHAR(50) NOT NULL CHECK (client_type IN ('individuel', 'famille', 'pmr')),
                        destination VARCHAR(50) NOT NULL CHECK (destination IN ('aeroport', 'gare', 'port', 'domicile')),
                        pickup_address TEXT NOT NULL,
                        pickup_datetime VARCHAR(50) NOT NULL,
                        bag_count VARCHAR(10) NOT NULL,
                        client_name VARCHAR(100) NOT NULL,
                        client_email VARCHAR(100) NOT NULL,
                        client_phone VARCHAR(20) NOT NULL,
                        special_instructions TEXT,
                        estimated_price DECIMAL(10,2) NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                # SQLite (local)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_type TEXT NOT NULL CHECK (client_type IN ('individuel', 'famille', 'pmr')),
                        destination TEXT NOT NULL CHECK (destination IN ('aeroport', 'gare', 'port', 'domicile')),
                        pickup_address TEXT NOT NULL,
                        pickup_datetime TEXT NOT NULL,
                        bag_count TEXT NOT NULL,
                        client_name TEXT NOT NULL,
                        client_email TEXT NOT NULL,
                        client_phone TEXT NOT NULL,
                        special_instructions TEXT,
                        estimated_price REAL NOT NULL,
                        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            # Index pour les performances
            conn.execute('CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_bookings_client_email ON bookings(client_email)')
            
            conn.commit()
            logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur initialisation base de données: {e}")
        # Ne pas faire planter l'app si la DB n'est pas prête

def require_admin(f):
    """Décorateur pour les routes admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_price(client_type, destination, bag_count, distance_km=0):
    """Calcul du prix selon les paramètres"""
    try:
        pricing = BASE_PRICING[client_type][destination]
        base_price = pricing['base']
        supplement = pricing['supplement']
        
        # Nombre de bagages
        bag_multiplier = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4+': 4
        }.get(bag_count, 1)
        
        # Calcul de base
        total = (base_price * bag_multiplier) + supplement
        
        # Ajout distance si applicable
        if distance_km > 10:  # Au-delà de 10km, tarif dégressif
            total += (distance_km - 10) * 0.5
        
        return round(total, 2)
    except KeyError:
        return 50.00  # Prix par défaut

def send_email(to_email, subject, message):
    """Envoi d'email"""
    if not EMAIL_PASS:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        return True
    except smtplib.SMTPException as e:
        logger.error(f"Erreur SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur email: {e}")
        return False

def get_distance_from_google(origin, destination):
    """Calcul de distance via Google Maps API"""
    if not GOOGLE_MAPS_API_KEY:
        return 15  # Distance par défaut
    
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': origin,
            'destinations': destination,
            'key': GOOGLE_MAPS_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            distance_m = data['rows'][0]['elements'][0]['distance']['value']
            return round(distance_m / 1000, 1)  # Conversion en km
        
    except requests.RequestException as e:
        logger.error(f"Erreur requête Google Maps: {e}")
    except Exception as e:
        logger.error(f"Erreur Google Maps: {e}")
    
    return 15  # Distance par défaut

def validate_email(email):
    """Validation du format email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validation du format téléphone français"""
    # Accepte les formats: 0123456789, +33123456789, 01 23 45 67 89, etc.
    pattern = r'^(?:(?:\+33|0)[1-9](?:[0-9]{8}))$'
    clean_phone = re.sub(r'[\s.-]', '', phone)
    return re.match(pattern, clean_phone) is not None

# Routes principales

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint de santé pour Railway"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/admin/simple-test')
def admin_simple_test():
    """Test simple sans base de données"""
    return """
    <h1>✅ Test Simple OK</h1>
    <p>Cette route fonctionne sans problème.</p>
    <p><a href="/admin/test">Test avec DB</a></p>
    <p><a href="/admin/login">Login Admin</a></p>
    """

@app.route('/admin/test')
def admin_test():
    """Test des routes admin"""
    try:
        # Test variables d'environnement
        db_url = os.environ.get('DATABASE_URL', 'Non définie')
        secret_key = 'Définie' if os.environ.get('SECRET_KEY') else 'Non définie'
        
        # Test templates
        import os
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        templates = os.listdir(template_dir)
        
        # Test connexion DB avec gestion d'erreur
        try:
            with get_db_connection() as conn:
                result = conn.execute('SELECT COUNT(*) as count FROM bookings').fetchone()
                db_status = f"✅ DB OK - {result[0]} réservations"
        except Exception as db_error:
            db_status = f"❌ DB ERROR: {str(db_error)}"
        
        return f"""
        <h1>🔧 Test Admin Routes</h1>
        <p><strong>Database URL:</strong> {db_url[:50]}...</p>
        <p><strong>Secret Key:</strong> {secret_key}</p>
        <p><strong>Database Status:</strong> {db_status}</p>
        <p><strong>Templates disponibles:</strong> {', '.join(templates)}</p>
        <p><strong>Session admin:</strong> {'Oui' if session.get('admin_logged_in') else 'Non'}</p>
        <hr>
        <p><a href="/admin/simple-test">Test Simple</a></p>
        <p><a href="/admin/login">Login Admin</a></p>
        <p><a href="/admin">Dashboard Admin</a></p>
        """
    except Exception as e:
        return f"❌ Erreur test: {str(e)}", 500

@app.route('/calculate-price', methods=['POST'])
def calculate_price_api():
    """API de calcul de prix"""
    try:
        data = request.get_json()
        
        client_type = data.get('client_type')
        destination = data.get('destination')
        bag_count = data.get('bag_count')
        pickup_address = data.get('pickup_address', '')
        
        # Calcul de distance si adresse fournie
        distance = 15  # Par défaut
        if pickup_address and destination != 'domicile':
            dest_addresses = {
                'aeroport': 'Aéroport Marseille Provence, Marignane',
                'gare': 'Gare Saint-Charles, Marseille',
                'port': 'Port de Marseille, Marseille'
            }
            destination_address = dest_addresses.get(destination, '')
            if destination_address:
                distance = get_distance_from_google(pickup_address, destination_address)
        
        price = calculate_price(client_type, destination, bag_count, distance)
        
        return jsonify({
            'success': True,
            'price': price,
            'distance': distance,
            'currency': 'EUR'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/book', methods=['POST'])
def book():
    """Création d'une nouvelle réservation"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = [
            'client_type', 'destination', 'pickup_address', 
            'pickup_datetime', 'bag_count', 'client_name', 
            'client_email', 'client_phone'
        ]
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Champ {field} requis'}), 400
        
        # Validation spécifique
        if not validate_email(data['client_email']):
            return jsonify({'success': False, 'error': 'Format email invalide'}), 400
        
        if not validate_phone(data['client_phone']):
            return jsonify({'success': False, 'error': 'Format téléphone invalide'}), 400
        
        # Calcul du prix
        distance = 15
        if data['pickup_address'] and data['destination'] != 'domicile':
            dest_addresses = {
                'aeroport': 'Aéroport Marseille Provence, Marignane',
                'gare': 'Gare Saint-Charles, Marseille',
                'port': 'Port de Marseille, Marseille'
            }
            destination_address = dest_addresses.get(data['destination'], '')
            if destination_address:
                distance = get_distance_from_google(data['pickup_address'], destination_address)
        
        estimated_price = calculate_price(
            data['client_type'], 
            data['destination'], 
            data['bag_count'], 
            distance
        )
        
        # Insertion en base
        with get_db_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO bookings (
                    client_type, destination, pickup_address, pickup_datetime,
                    bag_count, client_name, client_email, client_phone,
                    special_instructions, estimated_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['client_type'], data['destination'], data['pickup_address'],
                data['pickup_datetime'], data['bag_count'], data['client_name'],
                data['client_email'], data['client_phone'],
                data.get('special_instructions', ''), estimated_price
            ))
            
            booking_id = cursor.lastrowid
            conn.commit()
        
        # Envoi d'email de confirmation
        email_subject = f"2AV-Bagages - Confirmation de réservation #{booking_id}"
        email_message = f"""
        <h2>Bonjour {data['client_name']},</h2>
        <p>Votre réservation a été confirmée !</p>
        
        <h3>Détails de votre réservation :</h3>
        <ul>
            <li><strong>Numéro :</strong> #{booking_id}</li>
            <li><strong>Type :</strong> {data['client_type'].title()}</li>
            <li><strong>Destination :</strong> {data['destination'].title()}</li>
            <li><strong>Adresse de collecte :</strong> {data['pickup_address']}</li>
            <li><strong>Date/Heure :</strong> {data['pickup_datetime']}</li>
            <li><strong>Nombre de bagages :</strong> {data['bag_count']}</li>
            <li><strong>Prix estimé :</strong> {estimated_price}€</li>
        </ul>
        
        <p>Nous vous contacterons sous 24h pour confirmer votre réservation.</p>
        
        <p>Cordialement,<br>L'équipe 2AV-Bagages</p>
        <p>📞 (+33) 6-63-49-70-64</p>
        """
        
        send_email(data['client_email'], email_subject, email_message)
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'estimated_price': estimated_price
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Routes Admin

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Connexion admin"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASH.encode('utf-8')):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants incorrects', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@require_admin
def admin_dashboard():
    """Dashboard admin"""
    try:
        with get_db_connection() as conn:
            # Statistiques
            stats = {}
            stats['total_bookings'] = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
            stats['pending_bookings'] = conn.execute('SELECT COUNT(*) FROM bookings WHERE status = "pending"').fetchone()[0]
            stats['today_bookings'] = conn.execute('SELECT COUNT(*) FROM bookings WHERE DATE(created_at) = DATE("now")').fetchone()[0]
            
            revenue_result = conn.execute('SELECT SUM(estimated_price) FROM bookings WHERE status = "completed"').fetchone()
            stats['total_revenue'] = revenue_result[0] if revenue_result[0] else 0
            
            # Réservations récentes
            recent_bookings = conn.execute('''
                SELECT * FROM bookings 
                ORDER BY created_at DESC 
                LIMIT 10
            ''').fetchall()
        
        return render_template('admin_dashboard.html', stats=stats, recent_bookings=recent_bookings)
    except Exception as e:
        logger.error(f"Erreur dashboard admin: {e}")
        return f"Erreur dashboard: {str(e)}", 500

@app.route('/admin/bookings')
@require_admin
def admin_bookings():
    """Liste des réservations"""
    try:
        with get_db_connection() as conn:
            # Filtres
            status_filter = request.args.get('status', '')
            search = request.args.get('search', '')
            
            query = 'SELECT * FROM bookings WHERE 1=1'
            params = []
            
            if status_filter:
                query += ' AND status = ?'
                params.append(status_filter)
            
            if search:
                query += ' AND (client_name LIKE ? OR client_email LIKE ? OR client_phone LIKE ?)'
                search_param = f'%{search}%'
                params.extend([search_param, search_param, search_param])
            
            query += ' ORDER BY created_at DESC'
            
            bookings = conn.execute(query, params).fetchall()
        
        return render_template('admin_bookings.html', bookings=bookings, 
                             status_filter=status_filter, search=search)
    except Exception as e:
        logger.error(f"Erreur liste réservations: {e}")
        return f"Erreur réservations: {str(e)}", 500

@app.route('/admin/booking/<int:booking_id>/update-status', methods=['POST'])
@require_admin
def update_booking_status(booking_id):
    """Mise à jour du statut d'une réservation"""
    new_status = request.form['status']
    
    with get_db_connection() as conn:
        conn.execute('''
            UPDATE bookings 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (new_status, booking_id))
        conn.commit()
    
    flash(f'Statut mis à jour: {new_status}', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/api/bookings')
@require_admin
def api_bookings():
    """API JSON des réservations"""
    try:
        with get_db_connection() as conn:
            bookings = conn.execute('SELECT * FROM bookings ORDER BY created_at DESC').fetchall()
        
        return jsonify([dict(booking) for booking in bookings])
    except Exception as e:
        logger.error(f"Erreur API bookings: {e}")
        return jsonify({'error': str(e)}), 500

# Gestion des erreurs

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Initialisation pour Railway/Gunicorn
init_database()

# Point d'entrée pour développement local
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
    
