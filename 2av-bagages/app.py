from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MimeMultipart
import os
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # À changer en production
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# Base de données
def init_db():
    conn = sqlite3.connect('bagages.db')
    cursor = conn.cursor()
    
    # Table des réservations
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
    
    # Table des tarifs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_type TEXT NOT NULL,
            destination TEXT NOT NULL,
            base_price REAL NOT NULL,
            km_rate REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insérer les tarifs de base si la table est vide
    cursor.execute('SELECT COUNT(*) FROM pricing')
    if cursor.fetchone()[0] == 0:
        base_pricing = [
            ('pmr', 'aeroport', 30.0, 1.2),
            ('pmr', 'gare', 25.0, 1.2),
            ('pmr', 'port', 28.0, 1.2),
            ('pmr', 'domicile', 20.0, 1.2),
            ('famille', 'aeroport', 40.0, 1.5),
            ('famille', 'gare', 35.0, 1.5),
            ('famille', 'port', 38.0, 1.5),
            ('famille', 'domicile', 30.0, 1.5),
            ('individuel', 'aeroport', 35.0, 1.3),
            ('individuel', 'gare', 30.0, 1.3),
            ('individuel', 'port', 33.0, 1.3),
            ('individuel', 'domicile', 25.0, 1.3),
        ]
        cursor.executemany(
            'INSERT INTO pricing (client_type, destination, base_price, km_rate) VALUES (?, ?, ?, ?)',
            base_pricing
        )
    
    conn.commit()
    conn.close()

# Décorateur pour l'authentification admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Calculateur de distance (simulation - à remplacer par Google Maps API)
def calculate_distance(pickup_address, destination):
    """Calcule la distance entre deux points (simulation)"""
    # En production, utiliser Google Maps Distance Matrix API
    base_distances = {
        'aeroport': 25,  # km moyens vers l'aéroport
        'gare': 15,
        'port': 20,
        'domicile': 10
    }
    return base_distances.get(destination, 15)

# Calculateur de prix
def calculate_price(client_type, destination, pickup_address, bag_count):
    """Calcule le prix basé sur les paramètres"""
    conn = sqlite3.connect('bagages.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT base_price, km_rate FROM pricing WHERE client_type = ? AND destination = ?',
        (client_type, destination)
    )
    pricing = cursor.fetchone()
    conn.close()
    
    if not pricing:
        return 50.0  # Prix par défaut
    
    base_price, km_rate = pricing
    distance = calculate_distance(pickup_address, destination)
    
    # Calculer le prix
    total_price = base_price + (distance * km_rate)
    
    # Ajustements selon le nombre de bagages
    bag_multiplier = {
        '1': 1.0,
        '2': 1.3,
        '3': 1.6,
        '4+': 2.0
    }
    total_price *= bag_multiplier.get(bag_count, 1.0)
    
    return round(total_price, 2)

# Envoi d'email
def send_email(to_email, subject, body):
    """Envoie un email de confirmation"""
    try:
        msg = MimeMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MimeText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    """Traite une nouvelle réservation"""
    try:
        data = request.get_json()
        
        # Calculer le prix
        estimated_price = calculate_price(
            data['client_type'],
            data['destination'],
            data['pickup_address'],
            data['bag_count']
        )
        
        # Sauvegarder en base
        conn = sqlite3.connect('bagages.db')
        cursor = conn.cursor()
        
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
            data['bag_count'],
            data['client_name'],
            data['client_email'],
            data['client_phone'],
            data.get('special_instructions', ''),
            estimated_price
        ))
        
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Envoyer email de confirmation
        email_body = f"""
        <h2>Confirmation de réservation - 2AV Bagages</h2>
        <p>Bonjour {data['client_name']},</p>
        <p>Votre réservation a été confirmée avec succès !</p>
        
        <h3>Détails de votre réservation :</h3>
        <ul>
            <li><strong>N° de réservation :</strong> #{booking_id}</li>
            <li><strong>Type de client :</strong> {data['client_type'].title()}</li>
            <li><strong>Destination :</strong> {data['destination'].title()}</li>
            <li><strong>Adresse de collecte :</strong> {data['pickup_address']}</li>
            <li><strong>Date et heure :</strong> {data['pickup_datetime']}</li>
            <li><strong>Nombre de bagages :</strong> {data['bag_count']}</li>
            <li><strong>Prix estimé :</strong> {estimated_price}€</li>
        </ul>
        
        <p>Nous vous contacterons 30 minutes avant l'heure de collecte.</p>
        <p>Pour toute question : (+33) 6-63-49-70-64</p>
        
        <p>Cordialement,<br>L'équipe 2AV Bagages</p>
        """
        
        send_email(data['client_email'], 'Confirmation de réservation 2AV-Bagages', email_body)
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'estimated_price': estimated_price,
            'message': 'Réservation confirmée avec succès !'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la réservation: {str(e)}'
        }), 500

@app.route('/calculate-price', methods=['POST'])
def calculate_price_route():
    """Calcule le prix en temps réel"""
    try:
        data = request.get_json()
        price = calculate_price(
            data['client_type'],
            data['destination'],
            data.get('pickup_address', ''),
            data.get('bag_count', '1')
        )
        return jsonify({'price': price})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes d'administration
@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Identifiants incorrects', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('bagages.db')
    cursor = conn.cursor()
    
    # Statistiques
    cursor.execute('SELECT COUNT(*) FROM bookings')
    total_bookings = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM bookings WHERE status = "pending"')
    pending_bookings = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(estimated_price) FROM bookings WHERE status = "completed"')
    total_revenue = cursor.fetchone()[0] or 0
    
    # Réservations récentes
    cursor.execute('''
        SELECT * FROM bookings 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    recent_bookings = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings)

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    conn = sqlite3.connect('bagages.db')
    cursor = conn.cursor()
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    else:
        cursor.execute('SELECT * FROM bookings WHERE status = ? ORDER BY created_at DESC', (status_filter,))
    
    bookings = cursor.fetchall()
    conn.close()
    
    return render_template('admin_bookings.html', bookings=bookings, status_filter=status_filter)

@app.route('/admin/booking/<int:booking_id>/update-status', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    new_status = request.form.get('status')
    
    conn = sqlite3.connect('bagages.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (new_status, booking_id)
    )
    conn.commit()
    conn.close()
    
    flash(f'Statut mis à jour vers: {new_status}', 'success')
    return redirect(url_for('admin_bookings'))

# API Routes
@app.route('/api/bookings', methods=['GET'])
@admin_required
def api_bookings():
    conn = sqlite3.connect('bagages.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    bookings = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(zip([col[0] for col in cursor.description], booking)) for booking in bookings])

# Templates par défaut si pas de dossier templates
@app.errorhandler(404)
def not_found(error):
    return """
    <h1>404 - Page non trouvée</h1>
    <p><a href="/">Retour à l'accueil</a></p>
    """, 404

if __name__ == '__main__':
    init_db()
    
    # Port pour Railway (ou 5000 en local)
    port = int(os.environ.get('PORT', 5000))
    
    # Mode debug uniquement en local
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
  
