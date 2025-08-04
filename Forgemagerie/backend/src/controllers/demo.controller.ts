import { Request, Response } from 'express';
import { MockDataService } from '../services/mock-data.service';

export class DemoController {
  async getDemoRecommendations(req: Request, res: Response) {
    try {
      const { budget = 500000, preferredStats = ['vitalite', 'force'] } = req.body;

      // Données de démonstration hardcodées
      const demoRecommendations = {
        recommendations: [
          {
            item: {
              id: 1,
              name: "Gelano",
              type: "Anneau",
              level: 60,
              baseStats: { vitalite: 80, force: 15, intelligence: 15, chance: 15, agilite: 15 },
              maxStats: { vitalite: 120, force: 25, intelligence: 25, chance: 25, agilite: 25 },
              weight: 450,
              puits: 90
            },
            analysis: {
              expectedProfit: 45000,
              totalCost: 85000,
              profitability: 52.9,
              puitsUtilise: 45,
              targetStats: { vitalite: 100, force: 20 }
            },
            profitMargin: 52.9,
            investmentReturn: 0.53,
            difficulty: 'facile' as const,
            estimatedTime: 20,
            reasoning: "Excellente marge bénéficiaire • FM simple à réaliser • Stats recherchées sur le marché"
          },
          {
            item: {
              id: 3,
              name: "Bottes du Bouftou Royal",
              type: "Bottes",
              level: 100,
              baseStats: { vitalite: 200, force: 30, pm: 1 },
              maxStats: { vitalite: 300, force: 50, pm: 1 },
              weight: 800,
              puits: 160
            },
            analysis: {
              expectedProfit: 35000,
              totalCost: 120000,
              profitability: 29.2,
              puitsUtilise: 80,
              targetStats: { vitalite: 250, force: 45 }
            },
            profitMargin: 29.2,
            investmentReturn: 0.29,
            difficulty: 'moyen' as const,
            estimatedTime: 35,
            reasoning: "Bonne rentabilité • Item haut niveau très demandé • Stats recherchées sur le marché"
          },
          {
            item: {
              id: 5,
              name: "Amulette du Minotot",
              type: "Amulette",
              level: 80,
              baseStats: { vitalite: 150, force: 25, agilite: 25, pa: 1 },
              maxStats: { vitalite: 200, force: 40, agilite: 40, pa: 1 },
              weight: 750,
              puits: 150
            },
            analysis: {
              expectedProfit: 75000,
              totalCost: 180000,
              profitability: 41.7,
              puitsUtilise: 60,
              targetStats: { vitalite: 180, force: 35 }
            },
            profitMargin: 41.7,
            investmentReturn: 0.42,
            difficulty: 'moyen' as const,
            estimatedTime: 30,
            reasoning: "Excellente marge bénéficiaire • Stats recherchées sur le marché • Utilisation optimale du puits"
          }
        ],
        totalBudgetUsed: 385000,
        estimatedTotalProfit: 155000,
        marketAnalysis: {
          bestOpportunities: [
            "3 items avec +40% de marge identifiés",
            "2 opportunities faciles pour débuter"
          ],
          marketTrends: [
            "Anneau très demandé actuellement",
            "Stats PA/PM en forte hausse"
          ],
          warnings: []
        }
      };

      res.json({
        success: true,
        data: demoRecommendations,
        meta: {
          requestedBudget: budget,
          server: 'demo',
          generatedAt: new Date().toISOString(),
          note: 'Données de démonstration - Fonctionnalités complètes'
        }
      });

    } catch (error: any) {
      console.error('Erreur Demo Controller:', error);
      res.status(500).json({
        error: 'Erreur lors de la génération de la démo'
      });
    }
  }
}