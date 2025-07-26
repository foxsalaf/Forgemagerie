# 🚀 Guide de Déploiement Complet - 2AV-Bagages

## 📋 Checklist avant déploiement

### ✅ Prérequis
- [ ] Python 3.11+ installé
- [ ] Git configuré avec votre compte
- [ ] Compte Railway créé (railway.app)
- [ ] Compte Gmail avec mot de passe d'application généré
- [ ] Clé API Google Maps (optionnel mais recommandé)

## 🏗️ 1. Structure des fichiers

Créez cette structure dans votre projet :

```
2av-bagages/
├── app.py                      # Application Flask principale
├── requirements.txt            # Dépendances Python
├── Procfile                   # Configuration Railway
├── runtime.txt                # Version Python pour Railway
├── .env                       # Variables d'environnement (local)
├── .env.example              # Modèle de configuration
├── .gitignore                # Fichiers à ignorer Git
├── README.md                 # Documentation
├── templates/                # Templates Jinja2
│   ├── base.html            # Template de base
│   ├── index.html           # Page d'accueil
│   ├── admin_login.html     # Login admin
│   ├── admin_dashboard.html # Dashboard admin
│   ├── admin_bookings.html  # Gestion réservations
│   ├── 404.html            # Page erreur 404
│   └── 500.html            # Page erreur 500
└── database_complete.sql    # Script SQL initial (optionnel)
```

## 🔧 2. Configuration locale

### Créer le fichier `.env`
```env
# Sécurité
SECRET_KEY=your-super-secret-key-change-me-in-production
FLASK_ENV=development

# Administration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password

# Email (Gmail)
EMAIL_USER=2av.bagage@gmail.com
EMAIL_PASS=your-gmail-app-password

# APIs externes
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### Configuration Gmail
1. Activez l'authentification à 2 facteurs sur votre compte Gmail
2. Allez dans "Sécurité" → "Mots de passe des applications"
3. Générez un mot de passe pour "Application personnalisée"
4. Utilisez ce mot de passe dans `EMAIL_PASS`

### Configuration Google Maps (optionnel)
1. Allez sur [Google Cloud Console](https://console.cloud.google.com)
2. Créez un projet ou sélectionnez un projet existant
3. Activez l'API "Distance Matrix API"
4. Créez une clé API et ajoutez-la dans `GOOGLE_MAPS_API_KEY`

## 🧪 3. Test en local

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

Ouvrez http://localhost:5000 et testez :
- ✅ Page d'accueil s'affiche correctement
- ✅ Formulaire de réservation fonctionne
- ✅ Calcul de prix en temps réel
- ✅ Soumission de réservation
- ✅ Connexion admin (/admin/login)
- ✅ Dashboard admin fonctionne

## 🚀 4. Déploiement Railway

### A. Préparation Git
```bash
# 1. Initialiser le repository Git
git init

# 2. Ajouter tous les fichiers
git add .

# 3. Premier commit
git commit -m "🚀 Initial deployment - 2AV Bagages Platform"

# 4. Créer le repository sur GitHub
# Via interface GitHub ou CLI GitHub

# 5. Connecter origin
git remote add origin https://github.com/votre-username/2av-bagages.git
git branch -M main
git push -u origin main
```

### B. Déploiement Railway

1. **Connexion Railway**
   - Allez sur [railway.app](https://railway.app)
   - Connectez-vous avec GitHub
   - Cliquez "New Project"

2. **Import GitHub Repository**
   - Sélectionnez "Deploy from GitHub repo"
   - Choisissez votre repository `2av-bagages`
   - Railway détecte automatiquement Flask via `Procfile`

3. **Configuration des variables d'environnement**
   
   Dans Railway Dashboard → Variables, ajoutez :
   ```env
   SECRET_KEY=your-production-secret-key-super-secure
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-production-admin-password
   EMAIL_USER=2av.bagage@gmail.com
   EMAIL_PASS=your-gmail-app-password
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ```

4. **Ajout de PostgreSQL (recommandé pour production)**
   - Dans votre projet Railway, cliquez "+ New"
   - Sélectionnez "Database" → "PostgreSQL"
   - Railway génère automatiquement `DATABASE_URL`

### C. Configuration de la base de données

Railway va automatiquement créer les tables au premier lancement. Si vous souhaitez importer des données de test :

1. Allez dans Railway → Database → Query
2. Copiez-collez le contenu de `database_complete.sql`
3. Exécutez le script

## 🔄 5. Déploiement automatique

Railway redéploie automatiquement votre application à chaque push sur la branche `main` :

```bash
# Faire des modifications
git add .
git commit -m "✨ Nouvelle fonctionnalité"
git push origin main

# Railway détecte automatiquement et redéploie
```

## 🛠️ 6. Configuration DNS personnalisé (optionnel)

1. Dans Railway Dashboard → Settings → Domains
2. Cliquez "Custom Domain" 
3. Ajoutez votre domaine (ex: 2av-bagages.com)
4. Config