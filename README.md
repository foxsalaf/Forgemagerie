# 🚚 2AV-Bagages - Plateforme de Transport PACA

> Plateforme moderne de transport de bagages dans la région Aix-Marseille-Provence

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 🎯 Vue d'ensemble

2AV-Bagages est une plateforme web moderne qui révolutionne le transport de bagages dans la région PACA. Elle remplace un ancien système WordPress défaillant par une solution rapide, fiable et moderne.

### ✨ Fonctionnalités principales

- **🎨 Interface moderne** avec design glassmorphism et animations fluides
- **📱 Responsive design** optimisé mobile-first
- **🔄 Réservation intelligente** avec formulaire multi-étapes
- **💰 Calcul automatique** des tarifs selon distance et type
- **📧 Notifications email** automatiques
- **👨‍💼 Interface d'administration** complète
- **📊 Dashboard** avec statistiques temps réel
- **🚀 Déploiement facile** sur Railway avec Git

## 🏗️ Architecture technique

```
Frontend: HTML5/CSS3/JavaScript (Vanilla)
Backend: Python Flask
Database: SQLite (PostgreSQL en production)
Deployment: Railway + Git
APIs: Google Maps, Email (SMTP)
```

## 📦 Installation rapide

### Prérequis
- Python 3.11+
- Git
- Compte Railway (pour déploiement)

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/2av-bagages.git
cd 2av-bagages
```

### 2. Environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration
Créer un fichier `.env` :
```env
SECRET_KEY=votre-cle-secrete-ultra-secure
FLASK_ENV=development
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre-mot-de-passe-secure
EMAIL_USER=2av.bagage@gmail.com
EMAIL_PASS=votre-mot-de-passe-app-gmail
GOOGLE_MAPS_API_KEY=votre-cle-google-maps
```

### 5. Lancer l'application
```bash
python app.py
```

🎉 **L'application est disponible sur http://localhost:5000**

## 🚀 Déploiement sur Railway

### 1. Préparer le repository
```bash
git init
git add .
git commit -m "🚀 Initial deployment - 2AV Bagages"
git remote add origin https://github.com/votre-username/2av-bagages.git
git push -u origin main
```

### 2. Connecter à Railway
1. Aller sur [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Sélectionner votre repository
4. Railway détecte automatiquement Flask via `Procfile`

### 3. Variables d'environnement
Dans Railway Dashboard → Variables :
```
SECRET_KEY=votre-cle-production-ultra-secure
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre-mot-de-passe-production
EMAIL_USER=2av.bagage@gmail.com
EMAIL_PASS=votre-mot-de-passe-app-gmail
GOOGLE_MAPS_API_KEY=votre-cle-google-maps-api
```

### 4. Déploiement automatique
✅ Railway déploie automatiquement à chaque push sur `main`
✅ HTTPS automatique avec certificat SSL
✅ URL personnalisée disponible

## 📋 Structure du projet

```
2av-bagages/
├── 🐍 app.py                    # Backend Flask principal
├── 📋 requirements.txt          # Dépendances Python
├── 🚀 Procfile                 # Configuration Railway
├── 🐍 runtime.txt              # Version Python
├── 🚫 .gitignore               # Fichiers à ignorer
├── 📖 README.md                # Cette documentation
├── 📁 templates/               # Templates HTML Jinja2
│   ├── 🎨 base.html           # Template de base
│   ├── 🏠 index.html          # Page d'accueil
│   ├── 🔐 admin_login.html    # Connexion admin
│   ├── 📊 admin_dashboard.html # Dashboard admin
│   └── 📋 admin_bookings.html # Gestion réservations
├── 📁 static/                  # Fichiers statiques (si besoin)
│   ├── 🎨 css/
│   ├── ⚡ js/
│   └── 🖼️ images/
└── 🗄️ bagages.db              # Base SQLite (auto-créée)
```

## 🎨 Interface utilisateur

### 🏠 Page d'accueil
- Design glassmorphism moderne
- Particules animées en arrière-plan
- Formulaire de réservation intelligent en 4 étapes
- Calcul de prix en temps réel
- Responsive parfait mobile/desktop

### 👨‍💼 Interface admin
- Dashboard avec statistiques
- Gestion complète des réservations
- Filtres et recherche en temps réel
- Actions rapides (appel, email)
- Export des données

## 💾 Base de données

### Table `bookings`
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    client_type TEXT NOT NULL,      -- pmr, famille, individuel
    destination TEXT NOT NULL,      -- aeroport, gare, port, domicile
    pickup_address TEXT NOT NULL,
    pickup_datetime TEXT NOT NULL,
    bag_count TEXT NOT NULL,
    client_name TEXT NOT NULL,
    client_email TEXT NOT NULL,
    client_phone TEXT NOT NULL,
    special_instructions TEXT,
    estimated_price REAL,
    status TEXT DEFAULT 'pending',  -- pending, confirmed, completed, cancelled
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Table `pricing`
```sql
CREATE TABLE pricing (
    id INTEGER PRIMARY KEY,
    client_type TEXT NOT NULL,
    destination TEXT NOT NULL,
    base_price REAL NOT NULL,
    km_rate REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Page d'accueil |
| `POST` | `/book` | Nouvelle réservation |
| `POST` | `/calculate-price` | Calcul de prix |
| `GET` | `/admin` | Dashboard admin |
| `GET` | `/admin/bookings` | Liste réservations |
| `POST` | `/admin/booking/<id>/update-status` | Mise à jour statut |
| `GET` | `/api/bookings` | API JSON réservations |

## ⚙️ Configuration avancée

### Email avec Gmail
1. Activer l'authentification à 2 facteurs
2. Générer un "Mot de passe d'application"
3. Utiliser ce mot de passe dans `EMAIL_PASS`

### Google Maps API
1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. Activer "Distance Matrix API"
3. Créer une clé API
4. Ajouter dans `GOOGLE_MAPS_API_KEY`

### Base de données PostgreSQL (production)
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## 🎯 Tarification intelligente

Le système calcule automatiquement les prix selon :

- **Type de client** : PMR (réduction), Famille (majoration), Individuel (standard)
- **Destination** : Aéroport, Gare, Port, Domicile
- **Distance** : Calcul automatique Google Maps
- **Nombre de bagages** : Multiplicateur selon quantité

### Exemple de calcul
```python
Prix = (Prix_base + Distance_km × Taux_km) × Multiplicateur_bagages
```

## 🔮 Fonctionnalités futures (v2.0)

- [ ] 🗺️ **Géolocalisation temps réel** des véhicules
- [ ] 🤖 **IA de tarification** dynamique selon demande
- [ ] 📱 **Application mobile** native iOS/Android
- [ ] 🏷️ **QR codes** pour traçabilité bagages
- [ ] ⭐ **Système de notation** client/chauffeur
- [ ] 💳 **Paiement en ligne** Stripe
- [ ] 📈 **Analytics avancés** et reporting
- [ ] 🌍 **Multi-langues** (anglais, italien)
- [ ] 🔔 **Notifications push** en temps réel
- [ ] 📊 **API publique** pour partenaires

## 🛠️ Maintenance et monitoring

### Logs d'application
```bash
# Voir les logs Railway
railway logs

# Logs locaux
tail -f app.log
```

### Sauvegarde base de données
```python
# Script de sauvegarde automatique
import sqlite3
import datetime

def backup_database():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.system(f"cp bagages.db backup_bagages_{timestamp}.db")
```

### Monitoring performances
- Railway fournit automatiquement les métriques
- Monitoring uptime inclus
- Alertes automatiques en cas de problème

## 🔒 Sécurité

### Mesures implémentées
- ✅ Hash des mots de passe admin
- ✅ Protection CSRF
- ✅ Validation côté serveur
- ✅ Échappement XSS automatique (Jinja2)
- ✅ Variables d'environnement pour secrets
- ✅ HTTPS automatique (Railway)

### Bonnes pratiques
```python
# Jamais de secrets dans le code
SECRET_KEY = os.environ.get('SECRET_KEY')

# Validation stricte des entrées
email = request.json.get('email')
if not email or '@' not in email:
    return jsonify({'error': 'Email invalide'}), 400
```

## 📞 Support et contact

### Informations business
- **Téléphone** : (+33) 6-63-49-70-64
- **Email** : 2av.bagage@gmail.com
- **Zone** : Métropole Aix-Marseille-Provence

### Support technique
- **Issues GitHub** : [Créer un ticket](https://github.com/votre-username/2av-bagages/issues)
- **Documentation** : Ce README
- **Communauté** : [Discussions GitHub](https://github.com/votre-username/2av-bagages/discussions)

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Design inspiration** : Glassmorphism trend 2024
- **Framework** : Flask ecosystem
- **Hosting** : Railway.app
- **Icons** : Font Awesome
- **Typography** : Inter font family

---

## 🚀 Lancement rapide

```bash
# 1. Cloner
git clone https://github.com/votre-username/2av-bagages.git
cd 2av-bagages

# 2. Installer
pip install -r requirements.txt

# 3. Configurer
cp .env.example .env
# Éditer .env avec vos valeurs

# 4. Lancer
python app.py

# 5. Ouvrir
open http://localhost:5000
```

**🎉 Prêt à révolutionner le transport de bagages dans le PACA !**

---

*Fait avec ❤️ pour moderniser le transport de bagages*
