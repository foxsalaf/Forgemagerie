import { Router } from 'express';
import { AssistantController } from '../controllers/assistant.controller';

const router = Router();
const assistantController = new AssistantController();

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

export default router;