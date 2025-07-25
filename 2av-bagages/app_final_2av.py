#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 2AV-BAGAGES - Application Flask Finale
=========================================
Service de transport de bagages - Version Production
Corrigée grâce au Flask Debug Tool

Features:
- Interface client pour réservations
- Panel admin complet avec authentification BDD
- Calcul automatique des prix
- Notifications email
- Base de données PostgreSQL (Railway) / SQLite (local)
- API REST pour mises à jour
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# CONFIGURATION DE L'APPLICATION
# ============================================================================

app = Flask(__name__)

# Configuration sécurisée des clés
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variables d'environnement
DATABASE_URL = os.environ.get('DATABASE_URL')
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG_MODE = FLASK_ENV != 'production'

# ============================================================================
# CONFIGURATION BASE DE DONNÉES
# ============================================================================

def get_db_connection():
    """
    Connexion adaptative : PostgreSQL (Railway) ou SQLite (local)
    """
    try:
        if DATABASE_URL and 'postgresql' in DATABASE_URL:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Correction de l'URL PostgreSQL si nécessaire
            database_url = DATABASE_URL
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            logger.info("✅ Connexion PostgreSQL établie")
            return conn, 'postgresql'
        else:
            import sqlite3
            conn = sqlite3.connect('bagages.db')
            conn.row_factory = sqlite3.Row
            logger.info("✅ Connexion SQLite établie")
            return conn, 'sqlite'
    except Exception as e:
        logger.error(f"❌ Erreur connexion DB: {e}")
        raise

def execute_query(query, params=None, fetch_all=True, fetch_one=False):
    """
    Exécution sécurisée des requêtes avec gestion d'erreurs
    """
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

# ============================================================================
# FONCTIONS MÉTIER
# ============================================================================

def calculate_price(client_type, destination, bag_count):
    """
    Calcul des prix selon les tarifs 2AV-Bagages
    """
    try:
        bag_count = int(bag_count.replace('+', '')) if isinstance(bag_count, str) else int(bag_count)
        
        # Tarifs de base par type de client et destination
        tarifs = {
            'individuel': {
                'aeroport': 15.0,
                'gare': 12.0,
                'domicile': 18.0
            },
            'famille': {
                'aeroport': 25.0,
                'gare': 20.0,
                'domicile': 30.0
            },
            'pmr': {  # Personnes à mobilité réduite
                'aeroport': 20.0,
                'gare': 15.0,
                'domicile': 22.0
            }
        }
        
        base_price = tarifs.get(client_type, tarifs['individuel']).get(destination, 15.0)
        
        # Calcul avec nombre de bagages
        if bag_count <= 2:
            total = base_price
        else:
            # +5€ par bagage supplémentaire
            total = base_price + ((bag_count - 2) * 5.0)
        
        # Réduction famille nombreuse (>4 bagages)
        if client_type == 'famille' and bag_count > 4:
            total *= 0.9  # -10%
            
        return round(total, 2)
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul prix: {e}")
        return 20.0  # Prix par défaut

def send_email_notification(to_email, subject, body, booking_data=None):
    """
    Envoi de notifications email avec template
    """
    if not EMAIL_PASS or FLASK_ENV == 'development':
        logger.info(f"📧 Email simulé vers {to_email}: {subject}")
        return True
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Template HTML pour les emails
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                    <h1>🚀 2AV-Bagages</h1>
                    <p>Service de transport de bagages</p>
                </div>
                <div style="padding: 20px;">
                    <h2>{subject}</h2>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        {body}
                    </div>
                    {f'''
                    <h3>📋 Détails de votre réservation :</h3>
                    <ul>
                        <li><strong>Réservation :</strong> #{booking_data.get('id', 'N/A')}</li>
                        <li><strong>Client :</strong> {booking_data.get('client_name', 'N/A')}</li>
                        <li><strong>Date :</strong> {booking_data.get('pickup_datetime', 'N/A')}</li>
                        <li><strong>Adresse :</strong> {booking_data.get('pickup_address', 'N/A')}</li>
                        <li><strong>Destination :</strong> {booking_data.get('destination', 'N/A')}</li>
                        <li><strong>Bagages :</strong> {booking_data.get('bag_count', 'N/A')}</li>
                        <li><strong>Prix :</strong> {booking_data.get('estimated_price', 'N/A')}€</li>
                    </ul>
                    ''' if booking_data else ''}
                </div>
                <div style="background: #ecf0f1; padding: 15px; text-align: center; color: #7f8c8d;">
                    <p>📞 Contact: 06-63-49-70-64 | 📧 {EMAIL_USER}</p>
                    <p>Merci de faire confiance à 2AV-Bagages !</p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            
        logger.info(f"✅ Email envoyé vers {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi email: {e}")
        return False

# ============================================================================
# ROUTES PRINCIPALES - CLIENT
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil client avec formulaire de réservation"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"❌ Erreur chargement index: {e}")
        return f"""
        <h1>🚀 2AV-Bagages</h1>
        <p>Service de transport de bagages</p>
        <p>Erreur de chargement du template. Contact: 06-63-49-70-64</p>
        <a href="/admin/login">Administration</a>
        """, 500

@app.route('/booking', methods=['POST'])
def create_booking():
    """Création d'une nouvelle réservation"""
    try:
        # Récupération des données du formulaire
        data = {
            'client_type': request.form.get('client_type'),
            'client_name': request.form.get('client_name'),
            'client_email': request.form.get('client_email'),
            'client_phone': request.form.get('client_phone'),
            'pickup_address': request.form.get('pickup_address'),
            'destination': request.form.get('destination'),
            'pickup_datetime': request.form.get('pickup_datetime'),
            'bag_count': request.form.get('bag_count'),
            'special_instructions': request.form.get('special_instructions', '')
        }
        
        # Validation des champs obligatoires
        required_fields = ['client_type', 'client_name', 'client_email', 'client_phone', 
                          'pickup_address', 'destination', 'pickup_datetime', 'bag_count']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'message': f'Le champ {field} est requis'
                }), 400
        
        # Calcul du prix
        estimated_price = calculate_price(data['client_type'], data['destination'], data['bag_count'])
        
        # Insertion en base de données
        query = """
            INSERT INTO bookings (
                client_type, client_name, client_email, client_phone,
                pickup_address, destination, pickup_datetime, bag_count,
                special_instructions, estimated_price, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['client_type'], data['client_name'], data['client_email'], data['client_phone'],
            data['pickup_address'], data['destination'], data['pickup_datetime'], data['bag_count'],
            data['special_instructions'], estimated_price, 'en_attente', datetime.now()
        )
        
        execute_query(query, params, fetch_all=False)
        
        # Récupération de l'ID de la réservation créée
        booking_id_query = "SELECT id FROM bookings WHERE client_email = %s ORDER BY created_at DESC LIMIT 1"
        booking_result = execute_query(booking_id_query, (data['client_email'],), fetch_one=True)
        booking_id = booking_result['id'] if booking_result else 'N/A'
        
        # Envoi de l'email de confirmation
        email_subject = f"Confirmation de réservation 2AV-Bagages #{booking_id}"
        email_body = f"""
        <p>Bonjour <strong>{data['client_name']}</strong>,</p>
        <p>Votre réservation a été confirmée avec succès !</p>
        <p>Nous vous contacterons 30 minutes avant la collecte au {data['client_phone']}.</p>
        <p>À bientôt !</p>
        """
        
        booking_data = data.copy()
        booking_data.update({'id': booking_id, 'estimated_price': estimated_price})
        
        send_email_notification(data['client_email'], email_subject, email_body, booking_data)
        
        logger.info(f"✅ Réservation créée: #{booking_id} pour {data['client_name']}")
        
        return jsonify({
            'success': True,
            'message': 'Réservation confirmée !',
            'booking_id': booking_id,
            'estimated_price': estimated_price
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur création réservation: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la création de la réservation'
        }), 500

@app.route('/calculate-price', methods=['POST'])
def calculate_price_api():
    """API de calcul de prix en temps réel"""
    try:
        client_type = request.json.get('client_type')
        destination = request.json.get('destination')
        bag_count = request.json.get('bag_count')
        
        if not all([client_type, destination, bag_count]):
            return jsonify({'error': 'Paramètres manquants'}), 400
            
        price = calculate_price(client_type, destination, bag_count)
        
        return jsonify({
            'success': True,
            'price': price,
            'client_type': client_type,
            'destination': destination,
            'bag_count': bag_count
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul prix API: {e}")
        return jsonify({'error': 'Erreur de calcul'}), 500

# ============================================================================
# ROUTES ADMINISTRATION
# ============================================================================

@app.route('/admin/login')
def admin_login():
    """Page de connexion administrateur"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    try:
        return render_template('admin_login.html')
    except Exception as e:
        logger.error(f"❌ Erreur chargement admin login: {e}")
        return f"""
        <h1>🔐 Administration 2AV-Bagages</h1>
        <form method="post" action="/admin/auth">
            <p>Nom d'utilisateur: <input type="text" name="username" required></p>
            <p>Mot de passe: <input type="password" name="password" required></p>
            <p><button type="submit">Se connecter</button></p>
        </form>
        <p>Erreur de chargement du template admin.</p>
        """, 500

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    """Authentification administrateur avec base de données"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Nom d\'utilisateur et mot de passe requis', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        # Vérification dans la base de données
        query = "SELECT * FROM admin_users WHERE username = %s AND is_active = true"
        admin_user = execute_query(query, (username,), fetch_one=True)
        
        if admin_user and check_password_hash(admin_user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin_user['id']
            session['admin_username'] = admin_user['username']
            session['admin_role'] = admin_user.get('role', 'admin')
            
            logger.info(f"✅ Connexion admin réussie: {username}")
            flash(f'Bienvenue {admin_user["full_name"]} !', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            logger.warning(f"❌ Tentative de connexion échouée: {username}")
            flash('Identifiants incorrects', 'error')
            return redirect(url_for('admin_login'))
            
    except Exception as e:
        logger.error(f"❌ Erreur authentification admin: {e}")
        flash('Erreur de connexion', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion administrateur"""
    username = session.get('admin_username', 'Inconnu')
    session.clear()
    logger.info(f"📤 Déconnexion admin: {username}")
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    """Tableau de bord administrateur"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Statistiques rapides
        stats_query = """
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN status = 'en_attente' THEN 1 END) as pending_bookings,
                COUNT(CASE WHEN status = 'confirme' THEN 1 END) as confirmed_bookings,
                COUNT(CASE WHEN status = 'termine' THEN 1 END) as completed_bookings,
                COALESCE(SUM(estimated_price), 0) as total_revenue
            FROM bookings
        """
        stats = execute_query(stats_query, fetch_one=True)
        
        # Réservations récentes
        recent_query = """
            SELECT * FROM bookings 
            ORDER BY created_at DESC 
            LIMIT 10
        """
        recent_bookings = execute_query(recent_query)
        
        return render_template('admin_dashboard.html', 
                             stats=stats, 
                             recent_bookings=recent_bookings,
                             admin_username=session.get('admin_username'))
                             
    except Exception as e:
        logger.error(f"❌ Erreur dashboard admin: {e}")
        return f"""
        <h1>📊 Dashboard 2AV-Bagages</h1>
        <p>Bienvenue {session.get('admin_username', 'Admin')} !</p>
        <p><a href="/admin/bookings">Voir les réservations</a></p>
        <p><a href="/admin/logout">Déconnexion</a></p>
        <p>Erreur de chargement du template dashboard.</p>
        """, 500

@app.route('/admin/bookings')
def admin_bookings():
    """Gestion des réservations"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Filtres
        status_filter = request.args.get('status', 'all')
        search_filter = request.args.get('search', '')
        
        # Construction de la requête avec filtres
        base_query = "SELECT * FROM bookings WHERE 1=1"
        params = []
        
        if status_filter != 'all':
            base_query += " AND status = %s"
            params.append(status_filter)
        
        if search_filter:
            base_query += " AND (client_name ILIKE %s OR client_email ILIKE %s OR client_phone ILIKE %s)"
            search_param = f"%{search_filter}%"
            params.extend([search_param, search_param, search_param])
        
        base_query += " ORDER BY created_at DESC"
        
        bookings = execute_query(base_query, params if params else None)
        
        return render_template('admin_bookings.html', 
                             bookings=bookings,
                             current_status=status_filter,
                             current_search=search_filter,
                             admin_username=session.get('admin_username'))
                             
    except Exception as e:
        logger.error(f"❌ Erreur bookings admin: {e}")
        return f"""
        <h1>📋 Gestion des Réservations</h1>
        <p><a href="/admin">← Retour dashboard</a></p>
        <p>Erreur de chargement des réservations.</p>
        """, 500

@app.route('/admin/booking/<int:booking_id>/status', methods=['POST'])
def update_booking_status():
    """Mise à jour du statut d'une réservation (API)"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Non autorisé'}), 401
    
    try:
        booking_id = request.view_args['booking_id']
        new_status = request.json.get('status')
        
        if new_status not in ['en_attente', 'confirme', 'en_cours', 'termine', 'annule']:
            return jsonify({'error': 'Statut invalide'}), 400
        
        # Mise à jour du statut
        update_query = "UPDATE bookings SET status = %s, updated_at = %s WHERE id = %s"
        execute_query(update_query, (new_status, datetime.now(), booking_id), fetch_all=False)
        
        # Récupération des données pour email
        booking_query = "SELECT * FROM bookings WHERE id = %s"
        booking = execute_query(booking_query, (booking_id,), fetch_one=True)
        
        if booking and new_status in ['confirme', 'termine']:
            # Envoi d'email de notification
            status_messages = {
                'confirme': 'Votre réservation a été confirmée par notre équipe.',
                'termine': 'Votre transport a été effectué avec succès. Merci !'
            }
            
            email_subject = f"Mise à jour réservation 2AV-Bagages #{booking_id}"
            email_body = f"""
            <p>Bonjour <strong>{booking['client_name']}</strong>,</p>
            <p>{status_messages[new_status]}</p>
            <p>Statut: <strong>{new_status.replace('_', ' ').title()}</strong></p>
            """
            
            send_email_notification(booking['client_email'], email_subject, email_body)
        
        logger.info(f"✅ Statut mis à jour: Réservation #{booking_id} → {new_status}")
        
        return jsonify({
            'success': True,
            'message': f'Statut mis à jour: {new_status}',
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour statut: {e}")
        return jsonify({'error': 'Erreur de mise à jour'}), 500

# ============================================================================
# ROUTES API ET UTILITAIRES
# ============================================================================

@app.route('/api/stats')
def api_stats():
    """API des statistiques pour le dashboard"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Non autorisé'}), 401
    
    try:
        # Statistiques détaillées
        stats_query = """
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN status = 'en_attente' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'confirme' THEN 1 END) as confirmed,
                COUNT(CASE WHEN status = 'termine' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'annule' THEN 1 END) as cancelled,
                COALESCE(SUM(estimated_price), 0) as total_revenue,
                COALESCE(AVG(estimated_price), 0) as avg_price
            FROM bookings
        """
        stats = execute_query(stats_query, fetch_one=True)
        
        # Réservations par jour (7 derniers jours)
        daily_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as bookings_count,
                SUM(estimated_price) as daily_revenue
            FROM bookings 
            WHERE created_at >= %s
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 7
        """
        seven_days_ago = datetime.now() - timedelta(days=7)
        daily_stats = execute_query(daily_query, (seven_days_ago,))
        
        return jsonify({
            'success': True,
            'stats': dict(stats) if stats else {},
            'daily_stats': [dict(row) for row in daily_stats] if daily_stats else []
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur API stats: {e}")
        return jsonify({'error': 'Erreur récupération statistiques'}), 500

@app.route('/health')
def health_check():
    """Vérification de santé de l'application"""
    try:
        # Test de connexion à la base
        test_query = "SELECT 1"
        execute_query(test_query, fetch_one=True)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'environment': FLASK_ENV
        })
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ============================================================================
# GESTION D'ERREURS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Page d'erreur 404 personnalisée"""
    logger.warning(f"📄 404 - Page non trouvée: {request.path}")
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Page non trouvée | 2AV-Bagages</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            h1 { color: #e74c3c; }
            .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>404 - Page non trouvée</h1>
            <p>La page que vous cherchez n'existe pas.</p>
            <a href="/" class="btn">🏠 Accueil</a>
            <a href="/admin/login" class="btn">🔐 Administration</a>
        </div>
    </body>
    </html>
    """), 404

@app.errorhandler(500)
def internal_error(error):
    """Page d'erreur 500 personnalisée"""
    logger.error(f"💥 Erreur 500: {error}")
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Erreur Serveur | 2AV-Bagages</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            h1 { color: #e74c3c; }
            .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Erreur Temporaire</h1>
            <p>Nous rencontrons un problème technique temporaire.</p>
            <p>Veuillez réessayer dans quelques instants.</p>
            <p>Pour une urgence: 📞 06-63-49-70-64</p>
            <a href="/" class="btn">🏠 Accueil</a>
        </div>
    </body>
    </html>
    """), 500

# ============================================================================
# INITIALISATION ET DÉMARRAGE
# ============================================================================

def init_app_startup():
    """Initialisation au démarrage de l'application"""
    logger.info("🚀 Démarrage 2AV-Bagages")
    logger.info(f"📱 Environment: {FLASK_ENV}")
    logger.info(f"🗄️ Database: {'PostgreSQL' if DATABASE_URL and 'postgresql' in DATABASE_URL else 'SQLite'}")
    logger.info(f"📧 Email: {'Activé' if EMAIL_PASS else 'Mode simulation'}")
    
    # Test de connexion base de données
    try:
        conn, db_type = get_db_connection()
        conn.close()
        logger.info(f"✅ Connexion {db_type} testée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur test connexion DB: {e}")
    
    # Comptage des routes enregistrées
    routes_count = len(list(app.url_map.iter_rules()))
    logger.info(f"🗺️ {routes_count} routes enregistrées")
    
    # Vérification des variables critiques
    critical_vars = {
        'SECRET_KEY': bool(app.secret_key and app.secret_key != 'dev-secret-key-change-in-production'),
        'DATABASE_URL': bool(DATABASE_URL),
        'EMAIL_USER': bool(EMAIL_USER),
        'EMAIL_PASS': bool(EMAIL_PASS)
    }
    
    for var, status in critical_vars.items():
        status_icon = '✅' if status else '⚠️'
        logger.info(f"{status_icon} {var}: {'OK' if status else 'Manquant/Défaut'}")
    
    logger.info("🎯 Application 2AV-Bagages initialisée avec succès !")

def create_default_admin():
    """Création d'un admin par défaut si aucun n'existe"""
    try:
        # Vérifier s'il existe déjà un admin
        existing_admin = execute_query("SELECT COUNT(*) as count FROM admin_users", fetch_one=True)
        
        if existing_admin and existing_admin['count'] == 0:
            # Créer un admin par défaut
            default_username = os.environ.get('ADMIN_USERNAME', 'admin')
            default_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            password_hash = generate_password_hash(default_password)
            
            admin_query = """
                INSERT INTO admin_users (username, password_hash, email, full_name, role, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_query(admin_query, (
                default_username, 
                password_hash, 
                'admin@2av-bagages.com', 
                'Administrateur Principal',
                'admin',
                True
            ), fetch_all=False)
            
            logger.info(f"✅ Admin par défaut créé: {default_username}")
        else:
            logger.info("👤 Admin(s) existant(s) détecté(s)")
            
    except Exception as e:
        logger.warning(f"⚠️ Impossible de créer l'admin par défaut: {e}")

# ============================================================================
# ROUTES DE DÉVELOPPEMENT (uniquement en mode debug)
# ============================================================================

if DEBUG_MODE:
    @app.route('/dev/create-sample-data')
    def create_sample_data():
        """Création de données de test (développement uniquement)"""
        try:
            # Données de test
            sample_bookings = [
                {
                    'client_type': 'famille',
                    'client_name': 'Marie Dubois',
                    'client_email': 'marie.dubois@email.com',
                    'client_phone': '06-12-34-56-78',
                    'pickup_address': '123 Rue de la Paix, Paris',
                    'destination': 'aeroport',
                    'pickup_datetime': '2024-08-01 10:00:00',
                    'bag_count': '4',
                    'special_instructions': 'Bagages fragiles',
                    'estimated_price': 35.0,
                    'status': 'confirme'
                },
                {
                    'client_type': 'individuel',
                    'client_name': 'Jean Martin',
                    'client_email': 'jean.martin@email.com',
                    'client_phone': '06-98-76-54-32',
                    'pickup_address': '456 Avenue des Champs, Lyon',
                    'destination': 'gare',
                    'pickup_datetime': '2024-08-02 14:30:00',
                    'bag_count': '2',
                    'special_instructions': '',
                    'estimated_price': 12.0,
                    'status': 'en_attente'
                },
                {
                    'client_type': 'pmr',
                    'client_name': 'Sophie Bernard',
                    'client_email': 'sophie.bernard@email.com',
                    'client_phone': '06-55-44-33-22',
                    'pickup_address': '789 Boulevard Saint-Germain, Marseille',
                    'destination': 'domicile',
                    'pickup_datetime': '2024-08-03 16:00:00',
                    'bag_count': '1',
                    'special_instructions': 'Assistance PMR requise',
                    'estimated_price': 22.0,
                    'status': 'termine'
                }
            ]
            
            insert_query = """
                INSERT INTO bookings (
                    client_type, client_name, client_email, client_phone,
                    pickup_address, destination, pickup_datetime, bag_count,
                    special_instructions, estimated_price, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for booking in sample_bookings:
                execute_query(insert_query, (
                    booking['client_type'], booking['client_name'], booking['client_email'], 
                    booking['client_phone'], booking['pickup_address'], booking['destination'],
                    booking['pickup_datetime'], booking['bag_count'], booking['special_instructions'],
                    booking['estimated_price'], booking['status'], datetime.now()
                ), fetch_all=False)
            
            logger.info("✅ Données de test créées")
            return jsonify({
                'success': True,
                'message': f'{len(sample_bookings)} réservations de test créées',
                'data': sample_bookings
            })
            
        except Exception as e:
            logger.error(f"❌ Erreur création données test: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/dev/reset-admin')
    def reset_admin():
        """Réinitialisation de l'admin (développement uniquement)"""
        try:
            create_default_admin()
            return jsonify({
                'success': True,
                'message': 'Admin réinitialisé',
                'username': os.environ.get('ADMIN_USERNAME', 'admin'),
                'password': os.environ.get('ADMIN_PASSWORD', 'admin123')
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/dev/info')
    def dev_info():
        """Informations de développement"""
        return jsonify({
            'app_name': '2AV-Bagages',
            'version': '1.0.0',
            'environment': FLASK_ENV,
            'debug_mode': DEBUG_MODE,
            'database_type': 'PostgreSQL' if DATABASE_URL and 'postgresql' in DATABASE_URL else 'SQLite',
            'routes_count': len(list(app.url_map.iter_rules())),
            'email_configured': bool(EMAIL_PASS),
            'admin_username': os.environ.get('ADMIN_USERNAME', 'admin'),
            'routes': [{'rule': rule.rule, 'endpoint': rule.endpoint} for rule in app.url_map.iter_rules()]
        })

# ============================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ============================================================================

# Initialisation au niveau module (pour Gunicorn)
init_app_startup()

# Création de l'admin par défaut si nécessaire
try:
    create_default_admin()
except Exception as e:
    logger.warning(f"⚠️ Admin par défaut non créé: {e}")

# IMPORTANT: Toutes les routes DOIVENT être définies AVANT cette ligne
if __name__ == '__main__':
    # Mode développement local
    print("\n" + "="*80)
    print("🚀 2AV-BAGAGES - MODE DÉVELOPPEMENT LOCAL")
    print("="*80)
    print(f"🌐 URL: http://localhost:{os.environ.get('PORT', 5000)}")
    print(f"👤 Admin: {os.environ.get('ADMIN_USERNAME', 'admin')} / {os.environ.get('ADMIN_PASSWORD', 'admin123')}")
    print(f"📧 Email: {'Activé' if EMAIL_PASS else 'Mode simulation'}")
    print("🔧 Routes de développement disponibles:")
    print("   /dev/info - Informations système")
    print("   /dev/create-sample-data - Données de test")
    print("   /dev/reset-admin - Réinitialiser admin")
    print("="*80 + "\n")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
else:
    # Mode production (Railway/Gunicorn)
    logger.info("🌐 Mode production - Application prête pour les requêtes")

# ============================================================================
# DOCUMENTATION DES ROUTES
# ============================================================================

"""
📋 ROUTES DISPONIBLES:

🏠 CLIENT:
- GET  /                    → Page d'accueil avec formulaire de réservation
- POST /booking             → Création d'une nouvelle réservation
- POST /calculate-price     → API de calcul de prix en temps réel

🔐 ADMINISTRATION:
- GET  /admin/login         → Page de connexion administrateur
- POST /admin/auth          → Authentification administrateur
- GET  /admin/logout        → Déconnexion administrateur
- GET  /admin               → Tableau de bord administrateur
- GET  /admin/bookings      → Gestion des réservations
- POST /admin/booking/<id>/status → Mise à jour statut réservation (API)

📡 API:
- GET  /api/stats           → Statistiques pour dashboard (authentifié)
- GET  /health              → Vérification de santé de l'application

🛠️ DÉVELOPPEMENT (DEBUG_MODE uniquement):
- GET  /dev/info            → Informations système détaillées
- GET  /dev/create-sample-data → Création de données de test
- GET  /dev/reset-admin     → Réinitialisation admin par défaut

📄 GESTION D'ERREURS:
- 404 → Page personnalisée avec liens de navigation
- 500 → Page d'erreur avec contact d'urgence

🔧 VARIABLES D'ENVIRONNEMENT REQUISES:
- SECRET_KEY (obligatoire)
- DATABASE_URL (PostgreSQL pour production)
- EMAIL_USER (pour notifications)
- EMAIL_PASS (mot de passe application Gmail)
- ADMIN_USERNAME (optionnel, défaut: admin)
- ADMIN_PASSWORD (optionnel, défaut: admin123)
- FLASK_ENV (production/development)

🎯 FONCTIONNALITÉS:
✅ Interface client moderne avec calcul prix temps réel
✅ Panel admin complet avec authentification BDD
✅ Notifications email automatiques avec templates HTML
✅ Base de données adaptative (PostgreSQL/SQLite)
✅ API REST pour mises à jour de statut
✅ Gestion d'erreurs robuste
✅ Logging détaillé
✅ Mode développement avec outils de debug
✅ Health check pour monitoring
✅ Responsive design
✅ Sécurité (CSRF, validation, hashage mots de passe)
"""