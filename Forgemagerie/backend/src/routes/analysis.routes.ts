import { Router } from 'express';
import { AnalysisController } from '../controllers/analysis.controller';

const router = Router();
const analysisController = new AnalysisController();

router.post('/analyze', (req, res) => analysisController.analyzeItem(req, res));

router.get('/search', (req, res) => analysisController.searchItems(req, res));

router.get('/items/:id', (req, res) => analysisController.getItemDetails(req, res));

router.get('/runes', (req, res) => analysisController.getRunes(req, res));

router.post('/calculate-puits', (req, res) => analysisController.calculatePuits(req, res));

export default router;