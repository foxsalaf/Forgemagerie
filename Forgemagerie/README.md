# 🔨 Forgemagerie - Analyse de Rentabilité Dofus

Une application web complète pour analyser la rentabilité des forgemagie dans le jeu Dofus. Optimisez vos profits de joaillomage en temps réel avec des recommandations intelligentes de runes et des calculs précis de rentabilité.

## 🌟 Fonctionnalités

### ✨ Analyse Complète
- **Recherche d'objets** : Intégration avec l'API DofAPI pour accéder à tous les objets du jeu
- **Calcul du puits** : Calculs précis selon les règles officielles de Dofus
- **Recommandations de runes** : Sélection optimale des runes selon la densité et le coût
- **Scénarios détaillés** : Analyse des probabilités SC/SN/EC avec profits estimés

### 📊 Interface Moderne
- **Design responsive** : Interface adaptée desktop/mobile avec Tailwind CSS
- **Thème Dofus** : Couleurs et style inspirés du jeu
- **Temps réel** : Analyses instantanées avec indicateurs de chargement
- **Données live** : Prix HDV mis à jour automatiquement

### 🔧 Architecture Robuste
- **Backend TypeScript** : API REST sécurisée avec Express
- **Frontend Next.js** : Application React avec Server-Side Rendering
- **Base de données** : SQLite avec Prisma ORM
- **Tests** : Couverture complète avec Jest
- **CI/CD** : Pipeline automatisé avec GitHub Actions

## 🚀 Déploiement Rapide sur Railway

### Prérequis
- Compte [Railway](https://railway.app)
- Repository GitHub connecté

### Configuration Railway

1. **Créer un nouveau projet Railway**
```bash
# Connecter votre repository GitHub à Railway
```

2. **Variables d'environnement à configurer** :

```env
# Backend
PORT=3001
DATABASE_URL="postgresql://user:password@localhost:5432/forgemagerie"
NODE_ENV="production"

# APIs externes (optionnel)
DOFAPI_BASE_URL="https://api.dofusdb.fr"
DOFUSDUDE_API_KEY=""

# Frontend
NEXT_PUBLIC_API_URL="https://votre-app.railway.app"

# CORS
FRONTEND_URL="https://votre-app.railway.app"
```

3. **Déploiement automatique**
```bash
# Railway détecte automatiquement la configuration via railway.json
# Le déploiement se fait automatiquement à chaque push sur main
```

### 🔧 Variables d'Environnement Requises

Pour Railway, configurez ces variables dans votre dashboard :

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|---------|
| `PORT` | Port du serveur | `3001` | ✅ |
| `DATABASE_URL` | URL de la base de données PostgreSQL | Fournie par Railway | ✅ |
| `NODE_ENV` | Environnement | `production` | ✅ |
| `NEXT_PUBLIC_API_URL` | URL de l'API pour le frontend | URL Railway | ✅ |
| `FRONTEND_URL` | URL du frontend pour CORS | URL Railway | ✅ |
| `DOFAPI_BASE_URL` | URL de l'API DofAPI | `https://api.dofusdb.fr` | ❌ |
| `DOFUSDUDE_API_KEY` | Clé API DofusDude | `""` | ❌ |

## 💻 Installation Locale

### Prérequis
- Node.js 18+ 
- npm ou yarn

### Installation
```bash
# Cloner le repository
git clone https://github.com/votre-username/forgemagerie.git
cd forgemagerie

# Installer toutes les dépendances
npm run install:all

# Configuration environnement
cp backend/.env.example backend/.env
# Éditer backend/.env avec vos configurations

# Initialiser la base de données
cd backend
npm run db:generate
npm run db:migrate

# Démarrer en développement
cd ..
npm run dev
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:3001

## 📁 Structure du Projet

```
forgemagerie/
├── backend/                 # API Node.js/TypeScript
│   ├── src/
│   │   ├── controllers/     # Contrôleurs REST
│   │   ├── services/        # Logique métier
│   │   ├── routes/          # Routes Express
│   │   ├── types/           # Types TypeScript
│   │   └── __tests__/       # Tests unitaires
│   ├── prisma/              # Schéma base de données
│   └── package.json
├── frontend/                # Application Next.js/React
│   ├── src/
│   │   ├── app/             # Pages Next.js 13+
│   │   ├── components/      # Composants React
│   │   ├── services/        # Clients API
│   │   └── types/           # Types partagés
│   └── package.json
├── .github/workflows/       # CI/CD GitHub Actions
├── railway.json             # Configuration Railway
└── README.md
```

## 🧪 Tests

```bash
# Tests backend
cd backend
npm test

# Tests frontend  
cd frontend
npm test

# Couverture de code
npm run test -- --coverage
```

## 📚 API Documentation

### Endpoints Principaux

#### `POST /api/analysis/analyze`
Analyse complète d'un objet pour forgemagie.

```json
{
  "itemName": "Gelano",
  "targetStats": {
    "vitalite": 350,
    "agilite": 60
  },
  "statsASupprimer": {
    "sagesse": 20
  }
}
```

#### `GET /api/analysis/search?query=gelano`
Recherche d'objets par nom.

#### `GET /api/analysis/runes?type=ra&effect=vitalite`
Obtention des runes disponibles avec filtres.

#### `POST /api/analysis/calculate-puits`
Calcul du puits nécessaire pour des statistiques données.

### Format de Réponse
```json
{
  "success": true,
  "data": {
    "item": { /* Objet Dofus */ },
    "targetStats": { /* Stats cibles */ },
    "recommendedRunes": [ /* Runes recommandées */ ],
    "totalCost": 150000,
    "expectedProfit": 75000,
    "profitability": 33.5,
    "scenarios": [ /* Scénarios SC/SN/EC */ ],
    "puitsUtilise": 85,
    "puitsDisponible": 100
  }
}
```

## 🔧 Configuration Avancée

### Personnalisation des Calculs

Les règles de forgemagie sont configurables dans `backend/src/services/forge-magic.ts` :

```typescript
const config: ForgemagieConfig = {
  maxOverStats: {
    'vitalite': 40,
    'pa': 1,
    // ...
  },
  runeWeights: {
    'vitalite': 0.2,
    'pa': 100,
    // ...
  }
};
```

### Ajout de Nouvelles Runes

Modifier `backend/src/services/runes.service.ts` pour ajouter de nouvelles runes :

```typescript
{ 
  id: 200, 
  name: 'Nouvelle Rune', 
  effect: 'stat', 
  weight: 10, 
  density: 0.1, 
  type: 'ra', 
  price: 1000 
}
```

## 🐛 Dépannage

### Problèmes Courants

**Erreur de connexion API**
```bash
# Vérifier les variables d'environnement
echo $NEXT_PUBLIC_API_URL
```

**Base de données non initialisée**
```bash
cd backend
npx prisma db push
```

**Erreurs de build**
```bash
# Nettoyer les caches
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Guidelines de Développement

- **Tests** : Maintenir 80%+ de couverture de code
- **TypeScript** : Typage strict obligatoire
- **Commits** : Messages conventionnels (feat:, fix:, docs:)
- **Code Style** : ESLint + Prettier pour la cohérence

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **DofAPI** : Données des objets Dofus
- **DofusDude** : API alternative pour les données
- **Communauté Dofus** : Feedback et suggestions
- **Railway** : Hébergement cloud simplifié

## 📞 Support

- **Issues GitHub** : [Créer un ticket](https://github.com/votre-username/forgemagerie/issues)
- **Discussions** : [Forum du projet](https://github.com/votre-username/forgemagerie/discussions)

---

**⚡ Développé avec passion pour la communauté Dofus !**

🌟 N'hésitez pas à ⭐ ce projet s'il vous aide à optimiser vos forgemagie !