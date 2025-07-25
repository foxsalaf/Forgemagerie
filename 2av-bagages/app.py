#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌿 2AV-BAGAGES - Application Flask Production Finale
==================================================
Service de transport de bagages avec thème naturel
Toutes corrections appliquées pour Railway
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variables d'environnement
DATABASE_URL = os.environ.get('DATABASE_URL')
EMAIL_USER = os.environ.get('EMAIL_USER', '2av.bagage@gmail.com')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
DEBUG_MODE = FLASK_ENV != 'production'

# ============================================================================
# BASE DE DONNÉES ADAPTATIVE
# ============================================================================

def get_db_connection():
    """Connexion DB adaptative avec gestion d'erreurs"""
    try:
        if DATABASE_URL and 'postgresql' in DATABASE_URL:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = DATABASE_URL
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            return conn, 'postgresql'
        else:
            import sqlite3
            conn = sqlite3.connect('bagages.db')
            conn.row_factory = sqlite3.Row
            return conn, 'sqlite'
    except Exception as e:
        logger.error(f"Erreur connexion DB: {e}")
        raise

def execute_query(query, params=None, fetch_one=False):
    """Exécution sécurisée avec adaptation SQL"""
    try:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        # Adaptation des requêtes selon le type de DB
        if db_type == 'sqlite' and '%s' in query:
            query = query.replace('%s', '?')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchone() if fetch_one else cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Erreur requête: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return None

# ============================================================================
# FONCTIONS MÉTIER
# ============================================================================

def calculate_price(client_type, destination, bag_count):
    """Calcul des prix 2AV-Bagages"""
    try:
        bag_count = int(str(bag_count).replace('+', ''))
        
        tarifs = {
            'individuel': {'aeroport': 15.0, 'gare': 12.0, 'domicile': 18.0},
            'famille': {'aeroport': 25.0, 'gare': 20.0, 'domicile': 30.0},
            'pmr': {'aeroport': 20.0, 'gare': 15.0, 'domicile': 22.0}
        }
        
        base_price = tarifs.get(client_type, tarifs['individuel']).get(destination, 15.0)
        
        if bag_count <= 2:
            total = base_price
        else:
            total = base_price + ((bag_count - 2) * 5.0)
        
        if client_type == 'famille' and bag_count > 4:
            total *= 0.9
            
        return round(total, 2)
    except:
        return 20.0

def send_notification_email(to_email, subject, message, booking_data=None):
    """Envoi d'emails avec template naturel"""
    if not EMAIL_PASS or FLASK_ENV == 'development':
        logger.info(f"📧 Email simulé vers {to_email}: {subject}")
        return True
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Template HTML naturel
        html_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #87CEEB 0%, #98FB98 100%);">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #87CEEB 0%, #FF8C42 50%, #51CF66 100%); padding: 30px; text-align: center; color: white;">
                    <h1 style="margin: 0; font-size: 2.2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🌿 2AV-Bagages</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em;">Service de Transport Naturel</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #2E8B57; margin-top: 0; border-left: 4px solid #51CF66; padding-left: 15px;">{subject}</h2>
                    <div style="background: linear-gradient(135deg, #F0F8F0 0%, #E6F3FF 100%); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #87CEEB;">
                        {message}
                    </div>
                    {f'''
                    <div style="background: #FFF8DC; padding: 20px; border-radius: 10px; margin: 20px 0; border: 2px solid #DEB887;">
                        <h3 style="color: #8B4513; margin-top: 0;">🧳 Détails de votre réservation</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 8px 0; color: #556B2F;"><strong>Réservation :</strong></td><td style="color: #2E8B57;">#{booking_data.get('id', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; color: #556B2F;"><strong>Client :</strong></td><td style="color: #2E8B57;">{booking_data.get('client_name', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; color: #556B2F;"><strong>Date :</strong></td><td style="color: #2E8B57;">{booking_data.get('pickup_datetime', 'N/A')}</td></tr>
                            <tr><td style="padding: 8px 0; color: #556B2F;"><strong>Prix :</strong></td><td style="color: #FF8C42; font-weight: bold;">{booking_data.get('estimated_price', 'N/A')}€</td></tr>
                        </table>
                    </div>
                    ''' if booking_data else ''}
                </div>
                <div style="background: linear-gradient(135deg, #F5F5DC 0%, #E0E0E0 100%); padding: 25px; text-align: center; border-top: 3px solid #87CEEB;">
                    <div style="color: #2E8B57; margin: 5px 0;">
                        <span style="margin: 0 15px;">📱 06-63-49-70-64</span>
                        <span style="margin: 0 15px;">📧 {EMAIL_USER}</span>
                    </div>
                    <div style="margin-top: 15px; color: #8B4513; font-style: italic;">
                        🌱 Merci de faire confiance à 2AV-Bagages ! 🌱
                    </div>
                </div>
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
# TEMPLATES HTML INTÉGRÉS THÈME NATUREL
# ============================================================================

# CSS global thème naturel
NATURAL_CSS = """
<style>
:root {
    --bleu-ciel: #87CEEB; --bleu-clair: #B0E0E6;
    --orange-naturel: #FF8C42; --orange-doux: #FFA500;
    --vert-foret: #51CF66; --vert-clair: #69DB7C;
    --beige-terreux: #F5F5DC; --brun-doux: #DEB887;
    --vert-olive: #556B2F; --vert-sapin: #2E8B57;
    --rouge-automne: #FF6B6B; --jaune-soleil: #FFE066;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, var(--bleu-ciel) 0%, var(--vert-clair) 50%, var(--beige-terreux) 100%);
    min-height: 100vh; color: var(--vert-olive); line-height: 1.6;
}

.container { max-width: 1200px; margin: 0 auto; padding: 20px; }

.header {
    background: linear-gradient(135deg, var(--bleu-ciel) 0%, var(--orange-naturel) 50%, var(--vert-foret) 100%);
    color: white; padding: 30px; border-radius: 20px; margin-bottom: 30px;
    box-shadow: 0 15px 50px rgba(0,0,0,0.15); text-align: center;
}

.header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 3px 3px 6px rgba(0,0,0,0.3); }
.header p { font-size: 1.2em; opacity: 0.9; }

.card {
    background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 30px;
    margin-bottom: 25px; box-shadow: 0 15px 40px rgba(0,0,0,0.1);
    border-top: 4px solid var(--bleu-ciel); transition: all 0.3s ease;
}

.card:hover { transform: translateY(-5px); box-shadow: 0 20px 50px rgba(0,0,0,0.15); }

.form-group { margin: 20px 0; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--vert-sapin); font-size: 1.1em; }

.form-group input, .form-group select, .form-group textarea {
    width: 100%; padding: 15px; border: 2px solid var(--brun-doux); border-radius: 12px;
    font-size: 16px; background: linear-gradient(135deg, #FFFFFF 0%, var(--beige-terreux) 100%);
    transition: all 0.3s ease; color: var(--vert-olive);
}

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
    outline: none; border-color: var(--bleu-ciel);
    box-shadow: 0 0 20px rgba(135, 206, 235, 0.3); background: white;
}

.btn {
    display: inline-block; padding: 15px 30px; border: none; border-radius: 25px;
    font-size: 16px; font-weight: 600; text-decoration: none; cursor: pointer;
    transition: all 0.3s ease; margin: 10px 5px; text-align: center;
}

.btn-primary {
    background: linear-gradient(135deg, var(--bleu-ciel) 0%, var(--vert-foret) 100%);
    color: white; box-shadow: 0 8px 25px rgba(81, 207, 102, 0.3);
}

.btn-primary:hover {
    transform: translateY(-3px); box-shadow: 0 12px 35px rgba(81, 207, 102, 0.4);
    background: linear-gradient(135deg, var(--vert-foret) 0%, var(--bleu-ciel) 100%);
}

.btn-secondary {
    background: linear-gradient(135deg, var(--orange-naturel) 0%, var(--orange-doux) 100%);
    color: white; box-shadow: 0 8px 25px rgba(255, 140, 66, 0.3);
}

.btn-admin {
    background: linear-gradient(135deg, var(--vert-olive) 0%, var(--vert-sapin) 100%);
    color: white; box-shadow: 0 8px 25px rgba(85, 107, 47, 0.3);
}

.status-success {
    color: var(--vert-foret); font-weight: bold; font-size: 1.3em; padding: 15px;
    background: linear-gradient(135deg, rgba(81, 207, 102, 0.1) 0%, rgba(135, 206, 235, 0.1) 100%);
    border-radius: 12px; border-left: 5px solid var(--vert-foret); margin: 20px 0;
}

.info-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px; margin: 25px 0;
}

.info-item {
    background: linear-gradient(135deg, var(--beige-terreux) 0%, #FFFFFF 100%);
    padding: 20px; border-radius: 15px; border-left: 5px solid var(--bleu-ciel);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: all 0.3s ease;
}

.info-item:hover { transform: translateY(-3px); box-shadow: 0 12px 35px rgba(0,0,0,0.15); }
.info-item strong { display: block; color: var(--vert-sapin); margin-bottom: 8px; font-size: 1.1em; }

.price-display {
    background: linear-gradient(135deg, var(--orange-naturel) 0%, var(--jaune-soleil) 100%);
    color: white; font-size: 1.8em; font-weight: bold; padding: 20px;
    border-radius: 15px; text-align: center; margin: 20px 0;
    box-shadow: 0 10px 30px rgba(255, 140, 66, 0.3);
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.flash-message {
    padding: 15px 20px; border-radius: 12px; margin: 10px 0;
    font-weight: 500; border-left: 5px solid;
}

.flash-success {
    background: linear-gradient(135deg, rgba(81, 207, 102, 0.15) 0%, rgba(135, 206, 235, 0.15) 100%);
    color: var(--vert-sapin); border-left-color: var(--vert-foret);
}

.flash-error {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.15) 0%, rgba(255, 140, 66, 0.15) 100%);
    color: #D32F2F; border-left-color: var(--rouge-automne);
}

.natural-table {
    width: 100%; border-collapse: collapse; background: white;
    border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.natural-table th {
    background: linear-gradient(135deg, var(--vert-olive) 0%, var(--vert-sapin) 100%);
    color: white; padding: 15px; text-align: left; font-weight: 600;
}

.natural-table td { padding: 15px; border-bottom: 1px solid var(--brun-doux); color: var(--vert-olive); }
.natural-table tr:hover { background: linear-gradient(135deg, rgba(135, 206, 235, 0.1) 0%, rgba(245, 245, 220, 0.3) 100%); }

@media (max-width: 768px) {
    .container { padding: 15px; }
    .header h1 { font-size: 2em; }
    .info-grid { grid-template-columns: 1fr; }
    .btn { display: block; width: 100%; margin: 10px 0; }
}

@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeInUp 0.6s ease-out; }
</style>
"""

# Template page d'accueil
INDEX_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 2AV-Bagages - Transport Naturel de Bagages</title>
    {NATURAL_CSS}
</head>
<body>
    <div class="container">
        <div class="header fade-in">
            <h1>🌿 2AV-Bagages</h1>
            <p>Votre Service de Transport Naturel et Écologique</p>
        </div>
        
        <div class="card fade-in">
            <div class="status-success">
                ✅ Service disponible 7j/7 - Réservez votre transport écologique !
            </div>
            
            <h2 style="color: var(--vert-sapin); margin: 30px 0 20px 0; text-align: center;">
                🧳 Réserver un Transport
            </h2>
            
            <form method="post" action="/booking" id="bookingForm">
                <div class="info-grid">
                    <div class="form-group">
                        <label>🏷️ Type de Client :</label>
                        <select name="client_type" required onchange="updatePrice()">
                            <option value="">-- Choisir --</option>
                            <option value="individuel">👤 Individuel</option>
                            <option value="famille">👨‍👩‍👧‍👦 Famille</option>
                            <option value="pmr">♿ PMR (Mobilité Réduite)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>📍 Destination :</label>
                        <select name="destination" required onchange="updatePrice()">
                            <option value="">-- Choisir --</option>
                            <option value="aeroport">✈️ Aéroport</option>
                            <option value="gare">🚂 Gare</option>
                            <option value="domicile">🏠 Domicile</option>
                        </select>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="form-group">
                        <label>👤 Nom Complet :</label>
                        <input type="text" name="client_name" required placeholder="Votre nom complet">
                    </div>
                    
                    <div class="form-group">
                        <label>📧 Email :</label>
                        <input type="email" name="client_email" required placeholder="votre@email.com">
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="form-group">
                        <label>📱 Téléphone :</label>
                        <input type="tel" name="client_phone" required placeholder="06-XX-XX-XX-XX">
                    </div>
                    
                    <div class="form-group">
                        <label>🧳 Nombre de Bagages :</label>
                        <select name="bag_count" required onchange="updatePrice()">
                            <option value="">-- Choisir --</option>
                            <option value="1">1 bagage</option>
                            <option value="2">2 bagages</option>
                            <option value="3">3 bagages</option>
                            <option value="4">4 bagages</option>
                            <option value="5">5+ bagages</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>📍 Adresse de Collecte :</label>
                    <input type="text" name="pickup_address" required placeholder="Adresse complète de collecte">
                </div>
                
                <div class="form-group">
                    <label>🕐 Date et Heure :</label>
                    <input type="datetime-local" name="pickup_datetime" required>
                </div>
                
                <div class="form-group">
                    <label>📝 Instructions Spéciales :</label>
                    <textarea name="special_instructions" rows="3" placeholder="Bagages fragiles, étage, digicode, etc. (optionnel)"></textarea>
                </div>
                
                <div id="priceDisplay" class="price-display" style="display: none;">
                    💰 Prix estimé : <span id="priceAmount">--</span>€
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <button type="submit" class="btn btn-primary">🚀 Confirmer la Réservation</button>
                    <a href="/admin/login" class="btn btn-admin">🔐 Administration</a>
                </div>
            </form>
        </div>
        
        <div class="card">
            <div class="info-grid">
                <div class="info-item">
                    <strong>📞 Contact Direct</strong>
                    06-63-49-70-64
                </div>
                <div class="info-item">
                    <strong>📧 Email</strong>
                    2av.bagage@gmail.com
                </div>
                <div class="info-item">
                    <strong>🕐 Horaires</strong>
                    7j/7 - 5h00 à 20h30
                </div>
                <div class="info-item">
                    <strong>🌿 Service Écologique</strong>
                    Transport responsable
                </div>
            </div>
        </div>
    </div>

    <script>
    function updatePrice() {{
        const clientType = document.querySelector('[name="client_type"]').value;
        const destination = document.querySelector('[name="destination"]').value;
        const bagCount = document.querySelector('[name="bag_count"]').value;
        
        if (clientType && destination && bagCount) {{
            fetch('/calculate-price', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    client_type: clientType,
                    destination: destination,
                    bag_count: bagCount
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    document.getElementById('priceAmount').textContent = data.price;
                    document.getElementById('priceDisplay').style.display = 'block';
                }}
            }})
            .catch(error => console.error('Erreur:', error));
        }} else {{
            document.getElementById('priceDisplay').style.display = 'none';
        }}
    }}

    document.getElementById('bookingForm').addEventListener('submit', function(e) {{
        e.preventDefault();
        
        const formData = new FormData(this);
        
        fetch('/booking', {{
            method: 'POST',
            body: formData
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                alert('✅ Réservation confirmée !\\n\\nNuméro: #' + data.booking_id + '\\nPrix: ' + data.estimated_price + '€\\n\\nVous recevrez un email de confirmation.');
                this.reset();
                document.getElementById('priceDisplay').style.display = 'none';
            }} else {{
                alert('❌ ' + data.message);
            }}
        }})
        .catch(error => {{
            console.error('Erreur:', error);
            alert('❌ Erreur lors de la réservation. Veuillez réessayer.');
        }});
    }});
    </script>
</body>
</html>
"""

# Template connexion admin
ADMIN_LOGIN_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Administration - 2AV-Bagages</title>
    {NATURAL_CSS}
</head>
<body>
    <div class="container">
        <div style="max-width: 500px; margin: 100px auto;">
            <div class="card">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: var(--vert-sapin); margin-bottom: 10px;">🔐 Administration</h1>
                    <p style="color: var(--vert-olive);">2AV-Bagages - Panel Administrateur</p>
                </div>
                
                {{% if get_flashed_messages() %}}
                    <div>
                        {{% for category, message in get_flashed_messages(with_categories=true) %}}
                            <div class="flash-message flash-{{{{ category }}}}">
                                {{{{ message }}}}
                            </div>
                        {{% endfor %}}
                    </div>
                {{% endif %}}
                
                <form method="post" action="/admin/auth">
                    <div class="form-group">
                        <label>👤 Nom d'utilisateur :</label>
                        <input type="text" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label>🔒 Mot de passe :</label>
                        <input type="password" name="password" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" style="width: 100%;">
                        🚀 Se connecter
                    </button>
                </form>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="/" style="color: var(--vert-olive); text-decoration: none;">← Retour au site</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Template dashboard admin
ADMIN_DASHBOARD_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard - 2AV-Bagages</title>
    {NATURAL_CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard 2AV-Bagages</h1>
            <p>Bienvenue {{{{ admin_username }}}} !</p>
            <div style="margin-top: 15px;">
                <a href="/admin/bookings" class="btn btn-secondary">📋 Réservations</a>
                <a href="/admin/logout" class="btn" style="background: rgba(255,255,255,0.2);">📤 Déconnexion</a>
            </div>
        </div>
        
        {{% if get_flashed_messages() %}}
            <div>
                {{% for category, message in get_flashed_messages(with_categories=true) %}}
                    <div class="flash-message flash-{{{{ category }}}}">
                        {{{{ message }}}}
                    </div>
                {{% endfor %}}
            </div>
        {{% endif %}}
        
        <div class="info-grid">
            <div class="info-item">
                <strong>📋 Réservations Totales</strong>
                {{{{ stats.total_bookings if stats else 0 }}}}
            </div>
            <div class="info-item">
                <strong>⏳ En Attente</strong>
                {{{{ stats.pending_bookings if stats else 0 }}}}
            </div>
            <div class="info-item">
                <strong>✅ Confirmées</strong>
                {{{{ stats.confirmed_bookings if stats else 0 }}}}
            </div>
            <div class="info-item">
                <strong>💰 Revenus Totaux</strong>
                {{{{ "%.2f"|format(stats.total_revenue) if stats else "0.00" }}}}€
            </div>
        </div>
        
        <div class="card">
            <h3 style="color: var(--vert-sapin); margin-bottom: 20px;">📋 Réservations Récentes</h3>
            
            {{% if recent_bookings %}}
                <table class="natural-table">
                    <thead>
                        <tr>
                            <th>Client</th>
                            <th>Email</th>
                            <th>Destination</th>
                            <th>Prix</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{% for booking in recent_bookings %}}
                        <tr>
                            <td>{{{{ booking.client_name }}}}</td>
                            <td>{{{{ booking.client_email }}}}</td>
                            <td>{{{{ booking.destination.title() }}}}</td>
                            <td style="font-weight: bold; color: var(--orange-naturel);">{{{{ booking.estimated_price }}}}€</td>
                            <td>
                                <span style="padding: 5px 10px; border-radius: 10px; font-size: 0.9em; 
                                    background: {{% if booking.status == 'en_attente' %}}var(--jaune-soleil)
                                             {{% elif booking.status == 'confirme' %}}var(--vert-foret)
                                             {{% elif booking.status == 'termine' %}}var(--bleu-ciel)
                                             {{% else %}}var(--rouge-automne){{% endif %}};
                                    color: white;">
                                    {{{{ booking.status.replace('_', ' ').title() }}}}
                                </span>
                            </td>
                        </tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            {{% else %}}
                <div style="text-align: center; padding: 40px; color: var(--vert-olive);">
                    <h3>📭 Aucune réservation pour le moment</h3>
                    <p>Les nouvelles réservations apparaîtront ici.</p>
                </div>
            {{% endif %}}
            
            <div style="text-align: center; margin-top: 20px;">
                <a href="/admin/bookings" class="btn btn-primary">📋 Voir toutes les réservations</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil avec template intégré"""
    return INDEX_TEMPLATE

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
        
        execute_query(query, params)
        
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
        
        send_notification_email(data['client_email'], email_subject, email_body, booking_data)
        
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
    
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    """Authentification administrateur avec fallback"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Nom d\'utilisateur et mot de passe requis', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        # Essayer d'abord avec la base de données
        query = "SELECT * FROM admin_users WHERE username = %s AND is_active = true"
        admin_user = execute_query(query, (username,), fetch_one=True)
        
        if admin_user and check_password_hash(admin_user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin_user['id']
            session['admin_username'] = admin_user['username']
            session['admin_role'] = admin_user.get('role', 'admin')
            
            logger.info(f"✅ Connexion admin BDD réussie: {username}")
            flash(f'Bienvenue {admin_user["full_name"]} !', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Fallback sur les variables d'environnement
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_role'] = 'admin'
            
            logger.info(f"✅ Connexion admin ENV réussie: {username}")
            flash(f'Bienvenue {username} !', 'success')
            return redirect(url_for('admin_dashboard'))
        
        logger.warning(f"❌ Tentative de connexion échouée: {username}")
        flash('Identifiants incorrects', 'error')
        return redirect(url_for('admin_login'))
            
    except Exception as e:
        logger.error(f"❌ Erreur authentification admin: {e}")
        
        # Fallback final en cas d'erreur BDD
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash(f'Bienvenue {username} ! (Mode secours)', 'success')
            return redirect(url_for('admin_dashboard'))
        
        flash('Erreur de connexion', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    """Déconnexion administrateur"""
    username = session.get('admin_username', 'Inconnu')
    session.clear()
    logger.info(f"📤 Déconnexion admin: {username}")
    flash('Déconnexion réussie', 'success')
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
        recent_query = "SELECT * FROM bookings ORDER BY created_at DESC LIMIT 10"
        recent_bookings = execute_query(recent_query)
        
        return render_template_string(ADMIN_DASHBOARD_TEMPLATE, 
                                    stats=stats, 
                                    recent_bookings=recent_bookings,
                                    admin_username=session.get('admin_username'))
                             
    except Exception as e:
        logger.error(f"❌ Erreur dashboard admin: {e}")
        return f"""
        <!DOCTYPE html>
        <html><head><title>Dashboard 2AV-Bagages</title>{NATURAL_CSS}</head>
        <body><div class="container">
        <div class="header"><h1>📊 Dashboard 2AV-Bagages</h1>
        <p>Bienvenue {session.get('admin_username', 'Admin')} !</p></div>
        <div class="card">
        <p style="color: var(--rouge-automne);">⚠️ Erreur de chargement des données</p>
        <p>La base de données n'est peut-être pas encore initialisée.</p>
        <a href="/admin/logout" class="btn btn-secondary">Déconnexion</a>
        <a href="/" class="btn btn-primary">Retour au site</a>
        </div></div></body></html>
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
        
        # Template simple pour les réservations
        bookings_html = f"""
        <!DOCTYPE html>
        <html><head><title>Réservations - 2AV-Bagages</title>{NATURAL_CSS}</head>
        <body><div class="container">
        <div class="header">
            <h1>📋 Gestion des Réservations</h1>
            <div style="margin-top: 15px;">
                <a href="/admin" class="btn btn-secondary">← Dashboard</a>
                <a href="/admin/logout" class="btn" style="background: rgba(255,255,255,0.2);">Déconnexion</a>
            </div>
        </div>
        
        <div class="card">
            <div style="margin-bottom: 20px;">
                <form method="get" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                    <select name="status" onchange="this.form.submit()">
                        <option value="all"{'selected' if status_filter == 'all' else ''}>Tous les statuts</option>
                        <option value="en_attente"{'selected' if status_filter == 'en_attente' else ''}>En attente</option>
                        <option value="confirme"{'selected' if status_filter == 'confirme' else ''}>Confirmé</option>
                        <option value="termine"{'selected' if status_filter == 'termine' else ''}>Terminé</option>
                    </select>
                    <input type="text" name="search" placeholder="Rechercher..." value="{search_filter}">
                    <button type="submit" class="btn btn-primary">🔍 Filtrer</button>
                </form>
            </div>
        """
        
        if bookings:
            bookings_html += """
            <table class="natural-table">
                <thead>
                    <tr>
                        <th>ID</th><th>Client</th><th>Email</th><th>Téléphone</th>
                        <th>Destination</th><th>Bagages</th><th>Prix</th><th>Statut</th><th>Date</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for booking in bookings:
                status_color = {
                    'en_attente': 'var(--jaune-soleil)',
                    'confirme': 'var(--vert-foret)',
                    'termine': 'var(--bleu-ciel)',
                    'annule': 'var(--rouge-automne)'
                }.get(booking.get('status', ''), 'gray')
                
                bookings_html += f"""
                <tr>
                    <td>#{booking.get('id', 'N/A')}</td>
                    <td>{booking.get('client_name', 'N/A')}</td>
                    <td>{booking.get('client_email', 'N/A')}</td>
                    <td>{booking.get('client_phone', 'N/A')}</td>
                    <td>{booking.get('destination', 'N/A').title()}</td>
                    <td>{booking.get('bag_count', 'N/A')}</td>
                    <td style="font-weight: bold; color: var(--orange-naturel);">{booking.get('estimated_price', 'N/A')}€</td>
                    <td>
                        <span style="padding: 5px 10px; border-radius: 10px; background: {status_color}; color: white; font-size: 0.9em;">
                            {booking.get('status', 'N/A').replace('_', ' ').title()}
                        </span>
                    </td>
                    <td>{str(booking.get('created_at', 'N/A'))[:16] if booking.get('created_at') else 'N/A'}</td>
                </tr>
                """
            
            bookings_html += "</tbody></table>"
        else:
            bookings_html += """
            <div style="text-align: center; padding: 40px; color: var(--vert-olive);">
                <h3>📭 Aucune réservation trouvée</h3>
                <p>Aucune réservation ne correspond aux critères de recherche.</p>
            </div>
            """
        
        bookings_html += "</div></div></body></html>"
        
        return bookings_html
                             
    except Exception as e:
        logger.error(f"❌ Erreur bookings admin: {e}")
        return f"""
        <!DOCTYPE html>
        <html><head><title>Réservations - 2AV-Bagages</title>{NATURAL_CSS}</head>
        <body><div class="container">
        <div class="header"><h1>📋 Gestion des Réservations</h1></div>
        <div class="card">
        <p style="color: var(--rouge-automne);">⚠️ Erreur de chargement des réservations</p>
        <p>Erreur: {e}</p>
        <a href="/admin" class="btn btn-primary">← Retour dashboard</a>
        </div></div></body></html>
        """, 500

# ============================================================================
# ROUTES API ET UTILITAIRES
# ============================================================================

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
    return f"""
    <!DOCTYPE html>
    <html><head><title>404 - Page non trouvée</title>{NATURAL_CSS}</head>
    <body><div class="container">
    <div class="card" style="text-align: center; margin-top: 100px;">
        <h1 style="color: var(--rouge-automne);">404 - Page non trouvée</h1>
        <p>La page que vous cherchez n'existe pas.</p>
        <div style="margin-top: 20px;">
            <a href="/" class="btn btn-primary">🏠 Accueil</a>
            <a href="/admin/login" class="btn btn-admin">🔐 Administration</a>
        </div>
    </div></div></body></html>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    """Page d'erreur 500 personnalisée"""
    return f"""
    <!DOCTYPE html>
    <html><head><title>Erreur Serveur</title>{NATURAL_CSS}</head>
    <body><div class="container">
    <div class="card" style="text-align: center; margin-top: 100px;">
        <h1 style="color: var(--rouge-automne);">Erreur Temporaire</h1>
        <p>Nous rencontrons un problème technique temporaire.</p>
        <p>Veuillez réessayer dans quelques instants.</p>
        <p><strong>Pour une urgence: 📞 06-63-49-70-64</strong></p>
        <div style="margin-top: 20px;">
            <a href="/" class="btn btn-primary">🏠 Accueil</a>
        </div>
    </div></div></body></html>
    """, 500

# ============================================================================
# INITIALISATION ET DÉMARRAGE
# ============================================================================

def init_app_startup():
    """Initialisation au démarrage"""
    logger.info("🌿 Démarrage 2AV-Bagages - Version Finale")
    logger.info(f"📱 Environment: {FLASK_ENV}")
    logger.info(f"🗄️ Database: {'PostgreSQL' if DATABASE_URL and 'postgresql' in DATABASE_URL else 'SQLite'}")
    logger.info(f"📧 Email: {'Activé' if EMAIL_PASS else 'Mode simulation'}")
    
    # Test de connexion base de données
    try:
        conn, db_type = get_db_connection()
        conn.close()
        logger.info(f"✅ Connexion {db_type} testée avec succès")
    except Exception as e:
        logger.warning(f"⚠️ Test connexion DB échoué: {e}")
    
    # Comptage des routes enregistrées
    routes_count = len(list(app.url_map.iter_rules()))
    logger.info(f"🗺️ {routes_count} routes enregistrées")
    
    logger.info("🎯 Application 2AV-Bagages initialisée avec succès !")

def create_default_admin():
    """Création d'un admin par défaut si possible"""
    try:
        # Vérifier s'il existe déjà un admin
        existing_admin = execute_query("SELECT COUNT(*) as count FROM admin_users", fetch_one=True)
        
        if existing_admin and existing_admin['count'] == 0:
            # Créer un admin par défaut
            password_hash = generate_password_hash(ADMIN_PASSWORD)
            
            admin_query = """
                INSERT INTO admin_users (username, password_hash, email, full_name, role, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_query(admin_query, (
                ADMIN_USERNAME, 
                password_hash, 
                'admin@2av-bagages.com', 
                'Administrateur Principal',
                'admin',
                True
            ))
            
            logger.info(f"✅ Admin par défaut créé: {ADMIN_USERNAME}")
        else:
            logger.info("👤 Admin(s) existant(s) détecté(s)")
            
    except Exception as e:
        logger.info(f"ℹ️ Admin par défaut non créé (normal si BDD pas initialisée): {e}")

# ============================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ============================================================================

# Initialisation au niveau module (pour Gunicorn)
init_app_startup()

# Tentative de création de l'admin par défaut
create_default_admin()

# IMPORTANT: Toutes les routes DOIVENT être définies AVANT cette ligne
if __name__ == '__main__':
    # Mode développement local
    print("\n" + "="*80)
    print("🌿 2AV-BAGAGES - VERSION FINALE THÈME NATUREL")
    print("="*80)
    print(f"🌐 URL: http://localhost:{os.environ.get('PORT', 5000)}")
    print(f"👤 Admin: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print(f"📧 Email: {'Activé' if EMAIL_PASS else 'Mode simulation'}")
    print("🎯 Fonctionnalités:")
    print("   ✅ Interface client avec thème naturel")
    print("   ✅ Panel admin complet")
    print("   ✅ Calcul prix temps réel")
    print("   ✅ Notifications email")
    print("   ✅ Base de données adaptative")
    print("="*80 + "\n")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
else:
    # Mode production (Railway/Gunicorn)
    logger.info("🌐 Mode production - Application prête pour les requêtes")
        
