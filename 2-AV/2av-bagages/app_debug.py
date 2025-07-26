#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 APP_DEBUG.PY - Outil de Debug Flask Permanent
===============================================
Version avancée du mini Flask pour diagnostiquer les problèmes de déploiement.
À utiliser quand une app Flask ne fonctionne pas correctement.

Usage:
1. Remplacer temporairement app.py par ce fichier
2. Déployer sur Railway/Heroku/autre
3. Analyser les résultats via les pages de debug
4. Identifier le problème et corriger l'app principale

Créé pour le projet 2AV-Bagages - Peut être réutilisé pour tout projet Flask
"""

import os
import sys
import traceback
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request, session

# ============================================================================
# CONFIGURATION DEBUG
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'debug-secret-key-not-for-production')

# Informations système
DEBUG_MODE = os.environ.get('FLASK_ENV') != 'production'
START_TIME = datetime.now()

# ============================================================================
# TEMPLATES HTML AVANCÉS
# ============================================================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 Flask Debug Tool - {{ title }}</title>
    <style>
        :root {
            --primary: #3498db;
            --success: #27ae60;
            --warning: #f39c12;
            --danger: #e74c3c;
            --light: #ecf0f1;
            --dark: #2c3e50;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            margin-bottom: 25px;
            overflow: hidden;
        }
        
        .card-header {
            background: var(--primary);
            color: white;
            padding: 20px;
            font-size: 1.2em;
            font-weight: 600;
        }
        
        .card-body {
            padding: 25px;
        }
        
        .status-success { color: var(--success); font-weight: bold; }
        .status-warning { color: var(--warning); font-weight: bold; }
        .status-danger { color: var(--danger); font-weight: bold; }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .info-item {
            background: var(--light);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid var(--primary);
        }
        
        .info-item strong {
            display: block;
            color: var(--dark);
            margin-bottom: 5px;
        }
        
        .nav-menu {
            background: rgba(255,255,255,0.95);
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
        }
        
        .nav-menu ul {
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }
        
        .nav-menu a {
            color: var(--primary);
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 25px;
            background: rgba(52, 152, 219, 0.1);
            transition: all 0.3s ease;
        }
        
        .nav-menu a:hover {
            background: var(--primary);
            color: white;
            transform: translateY(-2px);
        }
        
        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            margin: 15px 0;
        }
        
        .route-list {
            display: grid;
            gap: 10px;
        }
        
        .route-item {
            background: rgba(52, 152, 219, 0.1);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid var(--primary);
        }
        
        .route-item strong {
            color: var(--primary);
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }
        
        .badge-success { background: var(--success); color: white; }
        .badge-warning { background: var(--warning); color: white; }
        .badge-danger { background: var(--danger); color: white; }
        
        @media (max-width: 768px) {
            .nav-menu ul { flex-direction: column; align-items: center; }
            .info-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-menu">
            <ul>
                <li><a href="/">🏠 Accueil</a></li>
                <li><a href="/debug">🔍 Debug Complet</a></li>
                <li><a href="/system">💻 Système</a></li>
                <li><a href="/database">🗄️ Base de Données</a></li>
                <li><a href="/test-all">🧪 Test Complet</a></li>
                <li><a href="/api/full-status">📡 API Status</a></li>
            </ul>
        </div>
        
        <div class="card">
            <div class="card-header">
                🔧 {{ title }}
            </div>
            <div class="card-body">
                {{ content | safe }}
            </div>
        </div>
    </div>
</body>
</html>
"""

# ============================================================================
# FONCTIONS UTILITAIRES DE DEBUG
# ============================================================================

def get_system_info():
    """Collecte les informations système détaillées"""
    return {
        'python_version': sys.version,
        'flask_version': getattr(Flask, '__version__', 'Inconnue'),
        'working_directory': os.getcwd(),
        'script_path': os.path.abspath(__file__),
        'uptime': str(datetime.now() - START_TIME),
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'port': os.environ.get('PORT', '5000'),
        'host': request.host if request else 'Inconnue'
    }

def get_environment_variables():
    """Analyse les variables d'environnement importantes"""
    important_vars = [
        'FLASK_ENV', 'PORT', 'SECRET_KEY', 'DATABASE_URL', 
        'EMAIL_USER', 'EMAIL_PASS', 'ADMIN_USERNAME', 'ADMIN_PASSWORD',
        'GOOGLE_MAPS_API_KEY', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID'
    ]
    
    env_status = {}
    for var in important_vars:
        value = os.environ.get(var)
        if value:
            # Masquer les valeurs sensibles
            if 'password' in var.lower() or 'secret' in var.lower() or 'key' in var.lower():
                env_status[var] = f"✅ Défini ({len(value)} caractères)"
            else:
                env_status[var] = f"✅ {value}"
        else:
            env_status[var] = "❌ Non défini"
    
    return env_status

def get_flask_routes():
    """Analyse détaillée des routes Flask"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': rule.rule,
            'endpoint': rule.endpoint,
            'methods': sorted(rule.methods),
            'has_defaults': bool(rule.defaults),
            'has_strict_slashes': rule.strict_slashes
        })
    return sorted(routes, key=lambda x: x['rule'])

def test_database_connection():
    """Test de connexion à la base de données"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return {'status': 'warning', 'message': 'DATABASE_URL non définie'}
        
        if 'postgresql' in database_url:
            try:
                import psycopg2
                # Adapter l'URL si nécessaire
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace('postgres://', 'postgresql://', 1)
                conn = psycopg2.connect(database_url)
                cursor = conn.cursor()
                cursor.execute('SELECT version()')
                version = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                return {'status': 'success', 'message': f'PostgreSQL connecté: {version[:50]}...'}
            except ImportError:
                return {'status': 'danger', 'message': 'psycopg2 non installé'}
            except Exception as e:
                return {'status': 'danger', 'message': f'Erreur PostgreSQL: {str(e)}'}
        else:
            return {'status': 'warning', 'message': 'Type de base de données non reconnu'}
            
    except Exception as e:
        return {'status': 'danger', 'message': f'Erreur générale: {str(e)}'}

# ============================================================================
# ROUTES DE DEBUG
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil avec vue d'ensemble"""
    system_info = get_system_info()
    env_vars = get_environment_variables()
    routes = get_flask_routes()
    db_status = test_database_connection()
    
    content = f"""
    <div class="status-success">✅ Flask Debug Tool fonctionne parfaitement !</div>
    
    <div class="info-grid">
        <div class="info-item">
            <strong>🌐 Environnement</strong>
            {system_info['environment']}
        </div>
        <div class="info-item">
            <strong>🚀 Uptime</strong>
            {system_info['uptime']}
        </div>
        <div class="info-item">
            <strong>🔗 Routes</strong>
            {len(routes)} routes enregistrées
        </div>
        <div class="info-item">
            <strong>🗄️ Base de Données</strong>
            <span class="status-{db_status['status']}">{db_status['message']}</span>
        </div>
    </div>
    
    <h3>🗺️ Routes Disponibles</h3>
    <div class="route-list">
    """
    
    for route in routes[:10]:  # Limiter l'affichage
        methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
        content += f"""
        <div class="route-item">
            <strong>{route['rule']}</strong> → {route['endpoint']} 
            <span class="badge badge-success">{methods}</span>
        </div>
        """
    
    content += "</div>"
    
    if len(routes) > 10:
        content += f"<p><em>... et {len(routes) - 10} autres routes. Voir <a href='/debug'>/debug</a> pour la liste complète.</em></p>"
    
    return render_template_string(BASE_TEMPLATE, title="Vue d'ensemble", content=content)

@app.route('/debug')
def debug_complete():
    """Page de debug complète"""
    system_info = get_system_info()
    env_vars = get_environment_variables()
    routes = get_flask_routes()
    
    content = f"""
    <h3>🔍 Informations Système Complètes</h3>
    <div class="info-grid">
        <div class="info-item">
            <strong>🐍 Version Python</strong>
            {system_info['python_version'].split()[0]}
        </div>
        <div class="info-item">
            <strong>⚡ Version Flask</strong>
            {system_info['flask_version']}
        </div>
        <div class="info-item">
            <strong>📁 Répertoire de Travail</strong>
            {system_info['working_directory']}
        </div>
        <div class="info-item">
            <strong>🌐 Host</strong>
            {system_info['host']}
        </div>
    </div>
    
    <h3>🔧 Variables d'Environnement</h3>
    <div class="route-list">
    """
    
    for var, status in env_vars.items():
        badge_class = "success" if "✅" in status else "danger"
        content += f"""
        <div class="route-item">
            <strong>{var}</strong>: 
            <span class="badge badge-{badge_class}">{status}</span>
        </div>
        """
    
    content += f"""
    </div>
    
    <h3>🗺️ Toutes les Routes ({len(routes)})</h3>
    <div class="route-list">
    """
    
    for route in routes:
        methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
        content += f"""
        <div class="route-item">
            <strong>{route['rule']}</strong> → {route['endpoint']}<br>
            <span class="badge badge-success">{methods}</span>
            {f'<span class="badge badge-warning">Defaults</span>' if route['has_defaults'] else ''}
        </div>
        """
    
    content += "</div>"
    
    return render_template_string(BASE_TEMPLATE, title="Debug Complet", content=content)

@app.route('/system')
def system_info():
    """Informations système détaillées"""
    system_info = get_system_info()
    
    content = f"""
    <h3>💻 Informations Système Détaillées</h3>
    
    <div class="code-block">
Python: {system_info['python_version']}
Flask: {system_info['flask_version']}
Répertoire: {system_info['working_directory']}
Script: {system_info['script_path']}
Uptime: {system_info['uptime']}
    </div>
    
    <h3>📂 Fichiers du Projet</h3>
    <div class="route-list">
    """
    
    try:
        files = os.listdir('.')
        for file in sorted(files):
            if os.path.isfile(file):
                size = os.path.getsize(file)
                content += f"""
                <div class="route-item">
                    <strong>{file}</strong> ({size} bytes)
                </div>
                """
    except Exception as e:
        content += f"<p class='status-danger'>Erreur lecture fichiers: {e}</p>"
    
    content += "</div>"
    
    return render_template_string(BASE_TEMPLATE, title="Informations Système", content=content)

@app.route('/database')
def database_test():
    """Test approfondi de la base de données"""
    db_status = test_database_connection()
    
    content = f"""
    <h3>🗄️ Test de Connexion Base de Données</h3>
    
    <div class="info-item">
        <strong>Statut</strong>
        <span class="status-{db_status['status']}">{db_status['message']}</span>
    </div>
    
    <h3>🔧 Configuration</h3>
    <div class="info-grid">
        <div class="info-item">
            <strong>DATABASE_URL</strong>
            {'✅ Définie' if os.environ.get('DATABASE_URL') else '❌ Non définie'}
        </div>
        <div class="info-item">
            <strong>Type détecté</strong>
            {'PostgreSQL' if os.environ.get('DATABASE_URL', '').find('postgresql') != -1 else 'Autre/Aucun'}
        </div>
    </div>
    """
    
    if os.environ.get('DATABASE_URL'):
        url = os.environ.get('DATABASE_URL')
        # Masquer les informations sensibles
        masked_url = url[:20] + '***' + url[-20:] if len(url) > 40 else '***'
        content += f"""
        <h3>📝 URL de Connexion (Masquée)</h3>
        <div class="code-block">{masked_url}</div>
        """
    
    return render_template_string(BASE_TEMPLATE, title="Test Base de Données", content=content)

@app.route('/test-all')
def test_all():
    """Test complet de toutes les fonctionnalités"""
    tests = []
    
    # Test 1: Routes
    routes = get_flask_routes()
    tests.append({
        'name': 'Routes Flask',
        'status': 'success' if len(routes) > 0 else 'danger',
        'message': f'{len(routes)} routes enregistrées'
    })
    
    # Test 2: Variables d'environnement critiques
    critical_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = [var for var in critical_vars if not os.environ.get(var)]
    tests.append({
        'name': 'Variables Critiques',
        'status': 'success' if not missing_vars else 'warning',
        'message': f'{len(critical_vars) - len(missing_vars)}/{len(critical_vars)} définies'
    })
    
    # Test 3: Base de données
    db_status = test_database_connection()
    tests.append({
        'name': 'Base de Données',
        'status': db_status['status'],
        'message': db_status['message']
    })
    
    # Test 4: Session
    try:
        session['test'] = 'ok'
        session_test = 'success'
        session_msg = 'Sessions fonctionnelles'
    except:
        session_test = 'danger'
        session_msg = 'Erreur sessions'
    
    tests.append({
        'name': 'Sessions Flask',
        'status': session_test,
        'message': session_msg
    })
    
    content = """
    <h3>🧪 Résultats des Tests Complets</h3>
    <div class="route-list">
    """
    
    for test in tests:
        badge_class = test['status']
        status_icon = '✅' if test['status'] == 'success' else '⚠️' if test['status'] == 'warning' else '❌'
        content += f"""
        <div class="route-item">
            <strong>{status_icon} {test['name']}</strong><br>
            <span class="badge badge-{badge_class}">{test['message']}</span>
        </div>
        """
    
    content += "</div>"
    
    overall_status = 'success' if all(t['status'] == 'success' for t in tests) else 'warning'
    content = f"""
    <div class="status-{overall_status}">
    {'🎉 Tous les tests sont OK !' if overall_status == 'success' else '⚠️ Certains tests nécessitent attention'}
    </div>
    """ + content
    
    return render_template_string(BASE_TEMPLATE, title="Tests Complets", content=content)

@app.route('/api/full-status')
def api_full_status():
    """API complète de statut (JSON)"""
    system_info = get_system_info()
    env_vars = get_environment_variables()
    routes = get_flask_routes()
    db_status = test_database_connection()
    
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'system': system_info,
        'environment_variables': env_vars,
        'routes': {
            'count': len(routes),
            'list': routes
        },
        'database': db_status,
        'debug_mode': DEBUG_MODE,
        'uptime': str(datetime.now() - START_TIME)
    })

# ============================================================================
# GESTION D'ERREURS AVANCÉE
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    content = f"""
    <div class="status-danger">❌ Page non trouvée</div>
    <p><strong>URL demandée:</strong> {request.path}</p>
    <p><strong>Méthode:</strong> {request.method}</p>
    <p><strong>Erreur:</strong> {error}</p>
    
    <h3>🗺️ Routes disponibles:</h3>
    <div class="route-list">
    """
    
    for rule in app.url_map.iter_rules():
        content += f"""
        <div class="route-item">
            <a href="{rule.rule}">{rule.rule}</a> → {rule.endpoint}
        </div>
        """
    
    content += "</div>"
    
    return render_template_string(BASE_TEMPLATE, title="404 - Page Non Trouvée", content=content), 404

@app.errorhandler(500)
def internal_error(error):
    content = f"""
    <div class="status-danger">❌ Erreur Serveur Interne</div>
    <p><strong>Erreur:</strong> {error}</p>
    
    <h3>🔍 Trace d'erreur:</h3>
    <div class="code-block">
    {traceback.format_exc()}
    </div>
    """
    
    return render_template_string(BASE_TEMPLATE, title="500 - Erreur Serveur", content=content), 500

# ============================================================================
# INITIALISATION ET DÉMARRAGE
# ============================================================================

def print_startup_info():
    """Affiche les informations de démarrage"""
    print("\n" + "="*80)
    print("🔧 FLASK DEBUG TOOL - DÉMARRAGE")
    print("="*80)
    print(f"🕐 Démarrage: {START_TIME}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"⚡ Flask: {getattr(Flask, '__version__', 'Inconnue')}")
    print(f"📱 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🌐 Port: {os.environ.get('PORT', '5000')}")
    print(f"🔑 Secret Key: {'✅ Défini' if os.environ.get('SECRET_KEY') else '❌ MANQUANT'}")
    print(f"🗄️ Database: {'✅ Défini' if os.environ.get('DATABASE_URL') else '❌ Non défini'}")
    
    print(f"\n🗺️ ROUTES ENREGISTRÉES ({len(list(app.url_map.iter_rules()))} total):")
    for rule in app.url_map.iter_rules():
        methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
        print(f"   {rule.rule:30} → {rule.endpoint:20} [{methods}]")
    
    print("="*80)
    print("✅ Debug Tool prêt ! Accédez aux pages de debug pour diagnostiquer.")
    print("="*80 + "\n")

# IMPORTANT: Toutes les routes DOIVENT être définies AVANT cette ligne
if __name__ == '__main__':
    print_startup_info()
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
else:
    # Mode production (Railway/Gunicorn)
    print_startup_info()
    
