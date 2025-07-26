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
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, jsonify, flash, g
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

# Configuration de l'application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuration
DATABASE = 'bagages.db'
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = hashlib.sha256(
    os.environ.get('ADMIN_PASSWORD', 'admin123').encode()
).hexdigest()

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

def get_db_connection():
    """Connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialisation de la base de données"""
    conn = get_db_connection()
    
    # Table des réservations
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
    conn.close()

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
    except Exception as e:
        print(f"Erreur email: {e}")
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
        
    except Exception as e:
        print(f"Erreur Google Maps: {e}")
    
    return 15  # Distance par défaut

# Routes principales

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint de santé pour Railway"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

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
        conn = get_db_connection()
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
        conn.close()
        
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
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
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
    conn = get_db_connection()
    
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
    
    conn.close()
    
    return render_template('admin_dashboard.html', stats=stats, recent_bookings=recent_bookings)

@app.route('/admin/bookings')
@require_admin
def admin_bookings():
    """Liste des réservations"""
    conn = get_db_connection()
    
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
    conn.close()
    
    return render_template('admin_bookings.html', bookings=bookings, 
                         status_filter=status_filter, search=search)

@app.route('/admin/booking/<int:booking_id>/update-status', methods=['POST'])
@require_admin
def update_booking_status():
    """Mise à jour du statut d'une réservation"""
    booking_id = request.form['booking_id']
    new_status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE bookings 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (new_status, booking_id))
    conn.commit()
    conn.close()
    
    flash(f'Statut mis à jour: {new_status}', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/api/bookings')
@require_admin
def api_bookings():
    """API JSON des réservations"""
    conn = get_db_connection()
    bookings = conn.execute('SELECT * FROM bookings ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return jsonify([dict(booking) for booking in bookings])

# Gestion des erreurs

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Point d'entrée

if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
    
