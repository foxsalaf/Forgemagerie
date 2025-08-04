import { Router } from 'express';
import { AssistantController } from '../controllers/assistant.controller';
import { DemoController } from '../controllers/demo.controller';

const router = Router();
const assistantController = new AssistantController();
const demoController = new DemoController();

// Route pour obtenir des recommandations personnalisées
router.post('/recommendations', (req, res) => {
  assistantController.getRecommendations(req, res);
});

// Route pour obtenir des insights du marché
router.get('/market-insights', (req, res) => {
  assistantController.getMarketInsights(req, res);
});

// Route pour valider un budget
router.post('/validate-budget', (req, res) => {
  assistantController.validateBudget(req, res);
});

// Route de test pour les données mockées
router.get('/test-mock-data', (req, res) => {
  const MockDataService = require('../services/mock-data.service').MockDataService;
  const items = MockDataService.getMockItems();
  res.json({
    success: true,
    data: {
      itemCount: items.length,
      items: items.slice(0, 3),
      message: 'Données mockées chargées avec succès'
    }
  });
});

// Route de démonstration avec données hardcodées
router.post('/demo-recommendations', (req, res) => {
  demoController.getDemoRecommendations(req, res);
});

export default router;