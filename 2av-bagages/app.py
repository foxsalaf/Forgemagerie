#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Flask App de Test pour Railway - Débogage 404
Créé pour diagnostiquer les problèmes de routage sur Railway
"""

import os
from flask import Flask, jsonify, render_template_string

# Création de l'app Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'test-secret-key-debug')

# Variables de debug
DEBUG_MODE = os.environ.get('FLASK_ENV') != 'production'

# Template HTML simple intégré pour éviter les erreurs de fichiers
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Flask Railway - {{ title }}</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 50px auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .status { 
            color: #27ae60; 
            font-weight: bold; 
            font-size: 1.2em;
        }
        .info { 
            background: #e8f4f8; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 15px 0;
        }
        .routes { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 15px 0;
        }
        .routes ul { 
            list-style-type: none; 
            padding: 0;
        }
        .routes li { 
            padding: 5px 0; 
            border-bottom: 1px solid #eee;
        }
        .routes a { 
            color: #3498db; 
            text-decoration: none;
        }
        .routes a:hover { 
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {{ title }}</h1>
        <p class="status">✅ Flask fonctionne correctement sur Railway !</p>
        
        <div class="info">
            <h3>📊 Informations de débogage :</h3>
            <ul>
                <li><strong>Environment :</strong> {{ env }}</li>
                <li><strong>Port :</strong> {{ port }}</li>
                <li><strong>Debug Mode :</strong> {{ debug }}</li>
                <li><strong>URL actuelle :</strong> {{ current_url }}</li>
            </ul>
        </div>

        <div class="routes">
            <h3>🗺️ Routes disponibles :</h3>
            <ul>
                <li><a href="/">/ - Page d'accueil</a></li>
                <li><a href="/test">/test - Page de test</a></li>
                <li><a href="/debug">/debug - Informations de debug</a></li>
                <li><a href="/api/status">/api/status - API Status (JSON)</a></li>
                <li><a href="/admin/test">/admin/test - Test admin</a></li>
            </ul>
        </div>
        
        {% if content %}
        <div class="info">
            <h3>📝 Contenu spécifique :</h3>
            {{ content | safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# ============================================================================
# ROUTES DE TEST
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil - Test de base"""
    return render_template_string(HTML_TEMPLATE, 
        title="2AV-Bagages - Test Railway",
        env=os.environ.get('FLASK_ENV', 'development'),
        port=os.environ.get('PORT', '5000'),
        debug=DEBUG_MODE,
        current_url="/"
    )

@app.route('/test')
def test():
    """Page de test simple"""
    return render_template_string(HTML_TEMPLATE,
        title="Page de Test",
        env=os.environ.get('FLASK_ENV', 'development'),
        port=os.environ.get('PORT', '5000'),
        debug=DEBUG_MODE,
        current_url="/test",
        content="<p>✅ Cette route fonctionne parfaitement !</p>"
    )

@app.route('/debug')
def debug_info():
    """Page de debug avec informations système"""
    debug_content = f"""
    <h4>🔍 Informations détaillées :</h4>
    <ul>
        <li><strong>Python Version :</strong> {os.sys.version}</li>
        <li><strong>Flask App Name :</strong> {app.name}</li>
        <li><strong>Working Directory :</strong> {os.getcwd()}</li>
        <li><strong>Environment Variables :</strong></li>
        <ul>
            <li>FLASK_ENV: {os.environ.get('FLASK_ENV', 'Non défini')}</li>
            <li>PORT: {os.environ.get('PORT', 'Non défini')}</li>
            <li>SECRET_KEY: {'✅ Défini' if os.environ.get('SECRET_KEY') else '❌ Non défini'}</li>
            <li>DATABASE_URL: {'✅ Défini' if os.environ.get('DATABASE_URL') else '❌ Non défini'}</li>
        </ul>
    </ul>
    
    <h4>🗺️ Routes enregistrées :</h4>
    <ul>
    """
    
    for rule in app.url_map.iter_rules():
        debug_content += f"<li><strong>{rule.rule}</strong> -> {rule.endpoint} ({', '.join(rule.methods)})</li>"
    
    debug_content += "</ul>"
    
    return render_template_string(HTML_TEMPLATE,
        title="Debug Information",
        env=os.environ.get('FLASK_ENV', 'development'),
        port=os.environ.get('PORT', '5000'),
        debug=DEBUG_MODE,
        current_url="/debug",
        content=debug_content
    )

@app.route('/api/status')
def api_status():
    """API JSON simple pour tester les routes API"""
    return jsonify({
        'status': 'success',
        'message': 'Flask API fonctionne correctement',
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'port': os.environ.get('PORT', '5000'),
        'routes_count': len(list(app.url_map.iter_rules())),
        'debug_mode': DEBUG_MODE
    })

@app.route('/admin/test')
def admin_test():
    """Test pour la section admin"""
    return render_template_string(HTML_TEMPLATE,
        title="Test Admin",
        env=os.environ.get('FLASK_ENV', 'development'),
        port=os.environ.get('PORT', '5000'),
        debug=DEBUG_MODE,
        current_url="/admin/test",
        content="<p>✅ Les routes admin fonctionnent !</p><p>Ceci confirme que le routage Flask est opérationnel.</p>"
    )

# ============================================================================
# GESTION D'ERREURS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Page d'erreur 404 personnalisée"""
    return render_template_string(HTML_TEMPLATE,
        title="404 - Page Non Trouvée",
        env=os.environ.get('FLASK_ENV', 'development'),
        port=os.environ.get('PORT', '5000'),
        debug=DEBUG_MODE,
        current_url="404 Error",
        content=f"""
        <p style="color: #e74c3c;">❌ La page demandée n'existe pas.</p>
        <p><strong>Erreur :</strong> {error}</p>
        <p><a href="/">← Retour à l'accueil</a></p>
        """
    ), 404

@app.errorhandler(500)
def internal_error(error):
    """Page d'erreur 500 personnalisée"""
    return render_template_string(HTML_TEMPLATE,
        title="500 - Erreur Serveur",
        env=os.environ.get('FLASK_ENV', 'development'),
        port=os.environ.get('PORT', '5000'),
        debug=DEBUG_MODE,
        current_url="500 Error",
        content=f"""
        <p style="color: #e74c3c;">❌ Erreur interne du serveur.</p>
        <p><strong>Erreur :</strong> {error}</p>
        <p><a href="/">← Retour à l'accueil</a></p>
        """
    ), 500

# ============================================================================
# FONCTION DE DEBUG AU DÉMARRAGE
# ============================================================================

def print_debug_info():
    """Affiche les informations de debug au démarrage"""
    print("\n" + "="*60)
    print("🚀 FLASK TEST APP - INFORMATIONS DE DEBUG")
    print("="*60)
    print(f"📱 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🌐 Port: {os.environ.get('PORT', '5000')}")
    print(f"🔑 Secret Key: {'✅ Défini' if os.environ.get('SECRET_KEY') else '❌ Non défini'}")
    print(f"🗄️ Database URL: {'✅ Défini' if os.environ.get('DATABASE_URL') else '❌ Non défini'}")
    print(f"🐛 Debug Mode: {DEBUG_MODE}")
    print("\n🗺️ ROUTES ENREGISTRÉES:")
    
    for rule in app.url_map.iter_rules():
        print(f"   {rule.rule} -> {rule.endpoint} ({', '.join(rule.methods)})")
    
    print("="*60)
    print("✅ App prête ! Toutes les routes sont enregistrées.")
    print("="*60 + "\n")

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

# IMPORTANT: Toutes les routes DOIVENT être définies AVANT cette ligne
if __name__ == '__main__':
    print_debug_info()
    # Mode développement local
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
else:
    # Mode production (Railway/Gunicorn)
    print_debug_info()
    
