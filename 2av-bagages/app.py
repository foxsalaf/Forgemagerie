from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Base de données - détection automatique SQLite/PostgreSQL
def get_db_connection():
    """Connexion adaptative SQLite ou PostgreSQL"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and 'postgresql' in database_url:
        # PostgreSQL pour Railway
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Fix pour Railway (remplacer postgres:// par postgresql://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn, 'postgresql'
    else:
        # SQLite pour développement local
        import sqlite3
        sqlite3.Row = sqlite3.Row  # Pour compatibilité
        conn = sqlite3.connect('bagages.db')
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def init_db():
    """Initialise la base de données (SQLite ou PostgreSQL)"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🗄️ Initialisation base de données {db_type}")
        
        if db_type == 'postgresql':
            # PostgreSQL syntax
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
            # SQLite syntax
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
        
        # Test de la connexion
        cursor.execute("SELECT COUNT(*) FROM bookings")
        count = cursor.fetchone()
        print(f"✅ Base de données {db_type} initialisée - {count[0] if count else 0} réservations")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur init DB: {e}")
        print(f"🔍 Variables disponibles: DATABASE_URL={os.environ.get('DATABASE_URL', 'Non définie')}")

# Décorateur pour l'authentification admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Calculateur de prix avec les vrais tarifs 2AV-Bagages
def calculate_price(client_type, destination, pickup_address, bag_count):
    """Calcule le prix basé sur les vrais tarifs 2AV-Bagages"""
    
    # Tarifs de base par bagage selon le type de client
    base_prices = {
        'pmr': 15.75,      # 63€ pour 4 bagages
        'famille': 13.75,  # 110€ pour 8 bagages  
        'individuel': 17   # 68€ pour 4 bagages
    }
    
    # Suppléments selon la destination
    destination_supplements = {
        'aeroport': 15,
        'gare': 8,
        'port': 12,
        'domicile': 5
    }
    
    # Prix de base par bagage
    price_per_bag = base_prices.get(client_type, 17)
    
    # Nombre de bagages
    if bag_count == '1':
        num_bags = 1
    elif bag_count == '2':
        num_bags = 2
    elif bag_count == '3':
        num_bags = 3
    elif bag_count == '4+':
        num_bags = 4
    else:
        num_bags = 1
    
    # Calcul total
    total_price = (price_per_bag * num_bags) + destination_supplements.get(destination, 10)
    
    return round(total_price, 2)

# Notification email simplifiée
def send_email_notification(to_email, subject, booking_details):
    """Log email au lieu de l'envoyer (temporaire)"""
    try:
        print(f"📧 EMAIL À ENVOYER:")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Booking: #{booking_details.get('booking_id', 'N/A')} - {booking_details.get('client_name', 'N/A')}")
        print("✅ Email logged")
        return True
    except Exception as e:
        print(f"❌ Erreur email: {e}")
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
        print(f"📦 Nouvelle réservation: {data}")
        
        # Validation des données
        if not data:
            return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
        
        required_fields = ['client_type', 'destination', 'pickup_address', 'client_name', 'client_email', 'client_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Champ {field} requis'}), 400
        
        # Calculer le prix
        estimated_price = calculate_price(
            data['client_type'],
            data['destination'],
            data['pickup_address'],
            data.get('bag_count', '1')
        )
        
        # Sauvegarder en base
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
        
        print(f"✅ Réservation #{booking_id} créée")
        
        # Notification email
        booking_info = data.copy()
        booking_info['booking_id'] = booking_id
        send_email_notification(
            data['client_email'], 
            f'Confirmation réservation 2AV-Bagages #{booking_id}',
            booking_info
        )
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'estimated_price': estimated_price,
            'message': 'Réservation confirmée avec succès !'
        })
        
    except Exception as e:
        print(f"❌ Erreur réservation: {e}")
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
            data.get('client_type', 'individuel'),
            data.get('destination', 'aeroport'),
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
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Statistiques
        cursor.execute('SELECT COUNT(*) FROM bookings')
        total_bookings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
        pending_bookings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(estimated_price), 0) FROM bookings WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0] or 0
        
        # Réservations récentes
        cursor.execute('''
            SELECT * FROM bookings 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_bookings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin_dashboard.html', 
                             total_bookings=total_bookings,
                             pending_bookings=pending_bookings,
                             total_revenue=float(total_revenue),
                             recent_bookings=recent_bookings)
                             
    except Exception as e:
        print(f"❌ Erreur dashboard: {e}")
        return f"Erreur: {e}", 500

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
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

# Route de test
@app.route('/test')
def test():
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bookings")
        count = cursor.fetchone()[0]
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

# Templates par défaut
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
# Ajoutez cette route à votre app.py existant, juste avant "if __name__ == '__main__':"

@app.route('/admin/update-status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    """Met à jour le statut d'une réservation"""
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
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }), 500
# Routes temporaires à ajouter dans votre app.py

@app.route('/debug-db')
def debug_database():
    """Debug de la connexion DB"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Test de connexion
        if db_type == 'postgresql':
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            
            # Vérifier si la table existe
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'bookings'
            """)
            table_exists = cursor.fetchone()
        else:
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='bookings'
            """)
            table_exists = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug 2AV-Bagages DB</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .success {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .error {{ background: #ffebee; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>🔍 Debug Base de Données 2AV-Bagages</h1>
            
            <div class="info">
                <strong>Type de DB:</strong> {db_type}<br>
                <strong>DATABASE_URL:</strong> {'Configurée' if database_url else 'Non définie'}<br>
                <strong>Version DB:</strong> {version[0] if version else 'Inconnue'}
            </div>
            
            <div class="{'success' if table_exists else 'error'}">
                <strong>Table 'bookings':</strong> {'✅ Existe' if table_exists else '❌ N\'existe pas'}
            </div>
            
            <p>
                <a href="/init-db" class="btn">🔧 Initialiser/Créer la table</a>
                <a href="/admin" class="btn" style="background: #28a745;">👤 Aller à l'admin</a>
            </p>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <h1>❌ Erreur de connexion</h1>
        <div style="background: #ffebee; padding: 15px; border-radius: 5px;">
            <strong>Erreur:</strong> {str(e)}<br>
            <strong>DATABASE_URL:</strong> {os.environ.get('DATABASE_URL', 'Non définie')[:50] if os.environ.get('DATABASE_URL') else 'Non définie'}
        </div>
        <p><a href="/">← Retour à l'accueil</a></p>
        """

@app.route('/init-db')
def init_database():
    """Route temporaire pour initialiser la DB"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🗄️ Initialisation de la base {db_type}")
        
        if db_type == 'postgresql':
            # Script PostgreSQL complet
            cursor.execute('''
                DROP TABLE IF EXISTS bookings CASCADE;
                
                CREATE TABLE bookings (
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
                );
            ''')
            
            # Index pour performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_client_type ON bookings(client_type);')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_destination ON bookings(destination);')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);')
            
            print("✅ Table PostgreSQL créée avec index")
            
        else:
            # Script SQLite
            cursor.execute('''
                DROP TABLE IF EXISTS bookings;
                
                CREATE TABLE bookings (
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
                );
            ''')
            print("✅ Table SQLite créée")
        
        # Insertion de données de test
        sample_bookings = [
            ('famille', 'aeroport', '123 Avenue des Champs-Élysées, 75008 Paris', 
             '2024-01-25 14:30', '4+', 'Marie Dubois', 'marie.dubois@gmail.com', 
             '06 12 34 56 78', 'Vol Air France AF1234 - Terminal 2E', 67.00, 'pending'),
            
            ('individuel', 'gare', '456 Rue de Rivoli, 75001 Paris', 
             '2024-01-25 09:15', '2', 'Jean Martin', 'j.martin@hotmail.fr', 
             '06 98 76 54 32', 'TGV 6651 Paris-Lyon départ 11:45', 42.00, 'confirmed'),
            
            ('pmr', 'domicile', '789 Boulevard Saint-Germain, 75006 Paris', 
             '2024-01-25 16:00', '3', 'Sophie Bernard', 'sophie.bernard@yahoo.fr', 
             '06 55 44 33 22', 'Fauteuil roulant nécessaire', 52.25, 'completed'),
        ]
        
        if db_type == 'postgresql':
            for booking in sample_bookings:
                cursor.execute('''
                    INSERT INTO bookings (
                        client_type, destination, pickup_address, pickup_datetime,
                        bag_count, client_name, client_email, client_phone,
                        special_instructions, estimated_price, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', booking)
        else:
            for booking in sample_bookings:
                cursor.execute('''
                    INSERT INTO bookings (
                        client_type, destination, pickup_address, pickup_datetime,
                        bag_count, client_name, client_email, client_phone,
                        special_instructions, estimated_price, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', booking)
        
        conn.commit()
        
        # Vérification
        cursor.execute("SELECT COUNT(*) FROM bookings")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Initialisation DB - 2AV-Bagages</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .success {{ background: #e8f5e8; padding: 20px; border-radius: 5px; border-left: 5px solid #4caf50; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }}
                .btn.success {{ background: #28a745; }}
            </style>
        </head>
        <body>
            <h1>✅ Base de données initialisée avec succès !</h1>
            
            <div class="success">
                <h3>Résumé de l'initialisation :</h3>
                <ul>
                    <li><strong>Type de DB:</strong> {db_type}</li>
                    <li><strong>Table 'bookings':</strong> Créée avec succès</li>
                    <li><strong>Index:</strong> Créés pour les performances</li>
                    <li><strong>Données de test:</strong> {count} réservations ajoutées</li>
                </ul>
            </div>
            
            <p>
                <a href="/admin" class="btn success">👤 Accéder à l'administration</a>
                <a href="/debug-db" class="btn">🔍 Vérifier la DB</a>
                <a href="/" class="btn">🏠 Retour à l'accueil</a>
            </p>
            
            <p><small><em>Note: Vous pouvez maintenant supprimer les routes /debug-db et /init-db de votre code.</em></small></p>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <h1>❌ Erreur lors de l'initialisation</h1>
        <div style="background: #ffebee; padding: 15px; border-radius: 5px;">
            <strong>Erreur:</strong> {str(e)}
        </div>
        <p><a href="/debug-db">← Retour au debug</a></p>
        """
if __name__ == '__main__':
    print("🚀 Démarrage 2AV-Bagages...")
    print(f"🗄️ Base de données: {os.environ.get('DATABASE_URL', 'SQLite local')}")
    
    # Initialiser la base
    init_db()
    
    # Démarrage serveur
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Serveur démarré sur port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
    
