import { DofapiService } from './dofapi.service';
import { RunesService } from './runes.service';
import { ForgemagieService } from './forgemagerie.service';
import { 
  AssistantRequest, 
  AssistantResponse, 
  AssistantRecommendation,
  DofusItem,
  ForgemagieAnalysis 
} from '../types';

export class AssistantService {
  private dofapiService: DofapiService;
  private runesService: RunesService;
  private forgemagieService: ForgemagieService;

  constructor() {
    this.dofapiService = new DofapiService();
    this.runesService = new RunesService();
    this.forgemagieService = new ForgemagieService();
  }

  async getRecommendations(request: AssistantRequest): Promise<AssistantResponse> {
    const recommendations: AssistantRecommendation[] = [];
    let totalBudgetUsed = 0;
    let estimatedTotalProfit = 0;

    // Étape 1: Rechercher les items populaires pour la joaillomagerie
    const popularItems = await this.findPopularJewelryItems(request);

    // Étape 2: Analyser chaque item potentiel
    for (const item of popularItems) {
      if (totalBudgetUsed >= request.budget * 0.9) break;

      try {
        const itemPrice = await this.dofapiService.getItemPrices(item.id);
        
        if (itemPrice > request.budget - totalBudgetUsed) continue;

        // Générer des stratégies de FM optimales
        const strategies = this.generateFMStrategies(item, request.preferredStats);

        for (const strategy of strategies) {
          const analysis = await this.forgemagieService.analyzeForgemagerie({
            item,
            targetStats: strategy.targetStats,
            statsASupprimer: strategy.statsASupprimer || {}
          });

          if (analysis.expectedProfit > 0 && 
              analysis.totalCost <= (request.budget - totalBudgetUsed) &&
              analysis.profitability >= (request.minProfitMargin || 10)) {
            
            const recommendation = this.createRecommendation(
              item, 
              analysis, 
              itemPrice, 
              request.riskTolerance
            );

            recommendations.push(recommendation);
            totalBudgetUsed += analysis.totalCost;
            estimatedTotalProfit += analysis.expectedProfit;

            if (recommendations.length >= 5) break;
          }
        }
      } catch (error) {
        console.error(`Erreur lors de l'analyse de l'item ${item.name}:`, error);
        continue;
      }
    }

    // Trier par rentabilité
    recommendations.sort((a, b) => b.investmentReturn - a.investmentReturn);

    const marketAnalysis = this.generateMarketAnalysis(recommendations, request.server);

    return {
      recommendations: recommendations.slice(0, 5),
      totalBudgetUsed,
      estimatedTotalProfit,
      marketAnalysis
    };
  }

  private async findPopularJewelryItems(request: AssistantRequest): Promise<DofusItem[]> {
    const jewelryTypes = [
      'Amulette', 'Anneau', 'Bottes', 'Ceinture', 'Cape',
      'Coiffe', 'Épée', 'Dague', 'Arc', 'Bâton', 'Marteau',
      'Pelle', 'Hache', 'Bouclier'
    ];

    const items: DofusItem[] = [];

    for (const type of jewelryTypes) {
      if (request.excludedTypes?.includes(type)) continue;

      try {
        const searchResults = await this.dofapiService.searchItem(type);
        
        for (const result of searchResults.slice(0, 10)) {
          const dofusItem = this.dofapiService.convertToDofusItem(result);
          
          if (request.maxItemLevel && dofusItem.level > request.maxItemLevel) continue;
          
          // Filtrer les items avec un bon potentiel de FM
          if (this.hasGoodFMPotential(dofusItem, request.preferredStats)) {
            items.push(dofusItem);
          }
        }
      } catch (error) {
        console.error(`Erreur lors de la recherche d'items ${type}:`, error);
      }
    }

    return items.slice(0, 50);
  }

  private hasGoodFMPotential(item: DofusItem, preferredStats: string[]): boolean {
    const itemStats = Object.keys(item.maxStats);
    const hasPreferredStats = preferredStats.some(stat => itemStats.includes(stat));
    const hasRoomForImprovement = item.puits >= 50;
    const goodStatCount = itemStats.length >= 3;

    return hasPreferredStats && hasRoomForImprovement && goodStatCount;
  }

  private generateFMStrategies(item: DofusItem, preferredStats: string[]): Array<{
    targetStats: Record<string, number>;
    statsASupprimer?: Record<string, number>;
  }> {
    const strategies = [];
    
    // Stratégie 1: Maximiser les stats préférées
    const maxStrategy: Record<string, number> = {};
    preferredStats.forEach(stat => {
      if (item.maxStats[stat]) {
        maxStrategy[stat] = Math.min(item.maxStats[stat] * 1.2, item.maxStats[stat] + 100);
      }
    });
    if (Object.keys(maxStrategy).length > 0) {
      strategies.push({ targetStats: maxStrategy });
    }

    // Stratégie 2: Amélioration progressive
    const progressiveStrategy: Record<string, number> = {};
    preferredStats.forEach(stat => {
      if (item.baseStats[stat]) {
        progressiveStrategy[stat] = Math.min(
          item.baseStats[stat] + 50,
          item.maxStats[stat] || item.baseStats[stat] + 50
        );
      }
    });
    if (Object.keys(progressiveStrategy).length > 0) {
      strategies.push({ targetStats: progressiveStrategy });
    }

    // Stratégie 3: Suppression + ajout (pour les items avec beaucoup de stats)
    if (Object.keys(item.baseStats).length > 6) {
      const lowValueStats: Record<string, number> = {};
      const highValueTargets: Record<string, number> = {};

      Object.entries(item.baseStats).forEach(([stat, value]) => {
        if (!preferredStats.includes(stat) && value < 20) {
          lowValueStats[stat] = Math.floor(value * 0.5);
        }
      });

      preferredStats.forEach(stat => {
        if (item.maxStats[stat]) {
          highValueTargets[stat] = item.maxStats[stat] * 1.1;
        }
      });

      if (Object.keys(lowValueStats).length > 0 && Object.keys(highValueTargets).length > 0) {
        strategies.push({
          targetStats: highValueTargets,
          statsASupprimer: lowValueStats
        });
      }
    }

    return strategies.slice(0, 3);
  }

  private createRecommendation(
    item: DofusItem,
    analysis: ForgemagieAnalysis,
    itemPrice: number,
    riskTolerance: string
  ): AssistantRecommendation {
    const profitMargin = (analysis.expectedProfit / analysis.totalCost) * 100;
    const investmentReturn = analysis.expectedProfit / itemPrice;
    
    let difficulty: 'facile' | 'moyen' | 'difficile' = 'moyen';
    let estimatedTime = 30; // minutes

    // Déterminer la difficulté basée sur le puits et les stats
    const puitsRatio = analysis.puitsUtilise / item.puits;
    const statsCount = Object.keys(analysis.targetStats).length;

    if (puitsRatio < 0.3 && statsCount <= 2) {
      difficulty = 'facile';
      estimatedTime = 15;
    } else if (puitsRatio > 0.7 || statsCount > 4) {
      difficulty = 'difficile';
      estimatedTime = 60;
    }

    // Ajuster selon la tolérance au risque
    if (riskTolerance === 'conservateur' && difficulty === 'difficile') {
      estimatedTime *= 1.5;
    }

    const reasoning = this.generateReasoning(item, analysis, profitMargin, difficulty);

    return {
      item,
      analysis,
      profitMargin,
      investmentReturn,
      difficulty,
      estimatedTime,
      reasoning
    };
  }

  private generateReasoning(
    item: DofusItem,
    analysis: ForgemagieAnalysis,
    profitMargin: number,
    difficulty: string
  ): string {
    const reasons = [];

    if (profitMargin > 50) {
      reasons.push("Excellente marge bénéficiaire");
    } else if (profitMargin > 25) {
      reasons.push("Bonne rentabilité");
    }

    if (difficulty === 'facile') {
      reasons.push("FM simple à réaliser");
    } else if (difficulty === 'difficile') {
      reasons.push("Stratégie avancée mais très rentable");
    }

    if (item.level >= 180) {
      reasons.push("Item haut niveau très demandé");
    }

    if (analysis.puitsUtilise / item.puits < 0.5) {
      reasons.push("Utilisation optimale du puits");
    }

    const preferredStats = ['pa', 'pm', 'portee', 'puissance', 'dommages'];
    const hasPreferredStats = preferredStats.some(stat => 
      Object.keys(analysis.targetStats).includes(stat)
    );
    
    if (hasPreferredStats) {
      reasons.push("Stats recherchées sur le marché");
    }

    return reasons.join(" • ");
  }

  private generateMarketAnalysis(recommendations: AssistantRecommendation[], server: string) {
    const bestOpportunities = [];
    const marketTrends = [];
    const warnings = [];

    // Analyser les opportunités
    const highProfitItems = recommendations.filter(r => r.profitMargin > 40);
    if (highProfitItems.length > 0) {
      bestOpportunities.push(`${highProfitItems.length} items avec +40% de marge identifiés`);
    }

    const easyItems = recommendations.filter(r => r.difficulty === 'facile');
    if (easyItems.length > 0) {
      bestOpportunities.push(`${easyItems.length} opportunities faciles pour débuter`);
    }

    // Tendances du marché
    const popularTypes = recommendations.reduce((acc, r) => {
      acc[r.item.type] = (acc[r.item.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const mostPopular = Object.entries(popularTypes)
      .sort(([,a], [,b]) => b - a)[0];
    
    if (mostPopular) {
      marketTrends.push(`${mostPopular[0]} très demandé actuellement`);
    }

    // Avertissements
    const highRiskItems = recommendations.filter(r => r.difficulty === 'difficile');
    if (highRiskItems.length > recommendations.length * 0.6) {
      warnings.push("Beaucoup d'items complexes - considérez commencer par les plus simples");
    }

    if (recommendations.length < 3) {
      warnings.push("Peu d'opportunités trouvées - considérez augmenter votre budget ou élargir vos critères");
    }

    return {
      bestOpportunities,
      marketTrends,
      warnings
    };
  }
}