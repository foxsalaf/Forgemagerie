import { Request, Response } from 'express';
import { AssistantService } from '../services/assistant.service';
import { AssistantRequest } from '../types';

export class AssistantController {
  private assistantService: AssistantService;

  constructor() {
    this.assistantService = new AssistantService();
  }

  async getRecommendations(req: Request, res: Response) {
    try {
      const {
        server = 'global',
        budget,
        preferredStats = [],
        riskTolerance = 'modere',
        minProfitMargin = 15,
        maxItemLevel = 200,
        excludedTypes = []
      } = req.body;

      // Validation des données
      if (!budget || budget <= 0) {
        return res.status(400).json({
          error: 'Le budget doit être un nombre positif'
        });
      }

      if (budget < 10000) {
        return res.status(400).json({
          error: 'Budget minimum de 10,000 kamas requis pour des recommandations pertinentes'
        });
      }

      if (!Array.isArray(preferredStats)) {
        return res.status(400).json({
          error: 'preferredStats doit être un tableau'
        });
      }

      const validRiskTolerances = ['conservateur', 'modere', 'agressif'];
      if (!validRiskTolerances.includes(riskTolerance)) {
        return res.status(400).json({
          error: 'riskTolerance doit être: conservateur, modere ou agressif'
        });
      }

      const assistantRequest: AssistantRequest = {
        server,
        budget,
        preferredStats,
        riskTolerance,
        minProfitMargin,
        maxItemLevel,
        excludedTypes
      };

      console.log(`🤖 Assistant: Recherche d'opportunités pour ${budget} kamas sur ${server}`);
      console.log(`📊 Critères: ${preferredStats.join(', ')} | Risque: ${riskTolerance}`);

      const recommendations = await this.assistantService.getRecommendations(assistantRequest);

      console.log(`✅ ${recommendations.recommendations.length} recommandations générées`);
      console.log(`💰 Profit estimé total: ${recommendations.estimatedTotalProfit.toLocaleString()} kamas`);

      res.json({
        success: true,
        data: recommendations,
        meta: {
          requestedBudget: budget,
          server,
          generatedAt: new Date().toISOString()
        }
      });

    } catch (error: any) {
      console.error('Erreur Assistant Controller:', error);
      res.status(500).json({
        error: 'Erreur lors de la génération des recommandations',
        details: process.env.NODE_ENV === 'development' ? error.message : undefined
      });
    }
  }

  async getMarketInsights(req: Request, res: Response) {
    try {
      const { server = 'global' } = req.query;

      // Simulation d'insights du marché basé sur des données historiques
      const insights = {
        hotItems: [
          { type: 'Amulette', demand: 'high', reason: 'Stats PA/PM très recherchées' },
          { type: 'Anneau', demand: 'medium', reason: 'Marché stable pour résistances' },
          { type: 'Bottes', demand: 'high', reason: 'PM en forte demande' }
        ],
        profitableStats: [
          { stat: 'pa', avgProfit: 45, difficulty: 'difficile' },
          { stat: 'pm', avgProfit: 42, difficulty: 'difficile' },
          { stat: 'puissance', avgProfit: 28, difficulty: 'moyen' },
          { stat: 'dommages', avgProfit: 25, difficulty: 'moyen' },
          { stat: 'vitalite', avgProfit: 18, difficulty: 'facile' }
        ],
        budgetRecommendations: {
          beginner: { min: 50000, recommended: 100000, description: 'Items simples, bonnes marges' },
          intermediate: { min: 200000, recommended: 500000, description: 'Diversification possible' },
          advanced: { min: 1000000, recommended: 2000000, description: 'Items haut niveau' }
        },
        serverSpecific: {
          server: server as string,
          marketActivity: 'normal',
          bestTimeToSell: '18h-22h',
          competitionLevel: 'moyen'
        }
      };

      res.json({
        success: true,
        data: insights,
        generatedAt: new Date().toISOString()
      });

    } catch (error: any) {
      console.error('Erreur Market Insights:', error);
      res.status(500).json({
        error: 'Erreur lors de la récupération des insights marché'
      });
    }
  }

  async validateBudget(req: Request, res: Response) {
    try {
      const { budget, riskTolerance = 'modere' } = req.body;

      if (!budget || budget <= 0) {
        return res.status(400).json({
          valid: false,
          message: 'Budget invalide'
        });
      }

      let recommendation = '';
      let category = '';

      if (budget < 50000) {
        category = 'insufficient';
        recommendation = 'Budget insuffisant. Minimum recommandé: 50,000 kamas pour commencer la joaillomagerie.';
      } else if (budget < 200000) {
        category = 'beginner';
        recommendation = 'Budget débutant. Concentrez-vous sur des items simples avec de bonnes marges.';
      } else if (budget < 1000000) {
        category = 'intermediate';
        recommendation = 'Budget intermédiaire. Vous pouvez diversifier sur plusieurs types d\'items.';
      } else {
        category = 'advanced';
        recommendation = 'Budget avancé. Accès aux items haut niveau et stratégies complexes.';
      }

      // Ajustements selon la tolérance au risque
      if (riskTolerance === 'conservateur') {
        recommendation += ' Privilégiez les stratégies à faible risque avec des marges stables.';
      } else if (riskTolerance === 'agressif') {
        recommendation += ' Vous pouvez tenter des stratégies plus risquées mais potentiellement très rentables.';
      }

      res.json({
        valid: budget >= 50000,
        category,
        recommendation,
        suggestedMinBudget: category === 'insufficient' ? 50000 : null
      });

    } catch (error: any) {
      console.error('Erreur Budget Validation:', error);
      res.status(500).json({
        error: 'Erreur lors de la validation du budget'
      });
    }
  }
}