import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import analysisRoutes from './routes/analysis.routes';
import assistantRoutes from './routes/assistant.routes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(helmet());
app.use(compression());

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

app.use('/api/analysis', analysisRoutes);
app.use('/api/assistant', assistantRoutes);

// Serve static frontend files
const frontendPath = path.join(__dirname, '../../frontend/.next/standalone');
const frontendStaticPath = path.join(__dirname, '../../frontend/.next/static');
const frontendPublicPath = path.join(__dirname, '../../frontend/public');

// Serve Next.js static files
app.use('/_next/static', express.static(frontendStaticPath));
app.use('/static', express.static(frontendPublicPath));

app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/api', (req, res) => {
  res.json({
    message: 'Forgemagerie API - Analyse de rentabilité Dofus',
    version: '1.0.0',
    endpoints: [
      'POST /api/analysis/analyze - Analyser un objet',
      'GET /api/analysis/search - Rechercher des objets',
      'GET /api/analysis/items/:id - Détails d\'un objet',
      'GET /api/analysis/runes - Obtenir les runes',
      'POST /api/analysis/calculate-puits - Calculer le puits'
    ]
  });
});

// Serve a simple frontend fallback
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Forgemagerie - Analyse de Rentabilité Dofus</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .card { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 10px; backdrop-filter: blur(10px); }
        .btn { display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }
        .btn:hover { background: #45a049; }
        .endpoint { background: rgba(0,0,0,0.2); padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="card">
          <h1>🔨 Forgemagerie</h1>
          <h2>Analyse de Rentabilité Dofus</h2>
          <p>API Backend déployée avec succès sur Railway!</p>
          
          <h3>🚀 Endpoints API Disponibles:</h3>
          <div class="endpoint">GET /health - Status de l'API</div>
          <div class="endpoint">GET /api - Documentation API</div>
          <div class="endpoint">GET /api/analysis/search?query=gelano - Rechercher objets</div>
          <div class="endpoint">GET /api/analysis/runes - Obtenir les runes</div>
          <div class="endpoint">POST /api/analysis/analyze - Analyser un objet</div>
          <div class="endpoint">POST /api/assistant/recommendations - Assistant IA</div>
          <div class="endpoint">GET /api/assistant/market-insights - Insights marché</div>
          
          <div style="margin-top: 2rem;">
            <a href="/health" class="btn">🏥 Health Check</a>
            <a href="/api" class="btn">📚 API Docs</a>
            <a href="/api/analysis/runes" class="btn">🔮 Voir les Runes</a>
          </div>
          
          <p style="margin-top: 2rem; font-size: 0.9em; opacity: 0.8;">
            Version 1.0.0 - PostgreSQL ✅ - Railway Deployment ✅
          </p>
        </div>
      </div>
    </body>
    </html>
  `);
});

app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint non trouvé',
    path: req.originalUrl
  });
});

app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Erreur serveur:', err);
  res.status(500).json({
    error: 'Erreur interne du serveur',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Serveur démarré sur le port ${PORT}`);
  console.log(`📋 Health check: http://localhost:${PORT}/health`);
  console.log(`🔍 API docs: http://localhost:${PORT}/`);
});

export default app;