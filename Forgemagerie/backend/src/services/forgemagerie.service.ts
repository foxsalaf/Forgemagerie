import { DofusItem, ForgemagieAnalysis, Rune } from '../types';
import { DofapiService } from './dofapi.service';
import { RunesService } from './runes.service';

export class ForgemagieService {
  private dofapiService: DofapiService;
  private runesService: RunesService;

  constructor() {
    this.dofapiService = new DofapiService();
    this.runesService = new RunesService();
  }

  async analyzeForgemagerie(data: {
    item: DofusItem;
    targetStats: Record<string, number>;
    statsASupprimer?: Record<string, number>;
  }): Promise<ForgemagieAnalysis> {
    const { item, targetStats, statsASupprimer = {} } = data;

    // Calculer le puits utilisé
    let puitsUtilise = 0;
    let puitsLibere = 0;

    // Calculer le puits libéré par suppression de stats
    Object.entries(statsASupprimer).forEach(([stat, value]) => {
      const currentValue = item.baseStats[stat] || 0;
      const reduction = Math.min(value, currentValue);
      const weight = this.getStatWeight(stat);
      puitsLibere += reduction * weight;
    });

    // Calculer le puits nécessaire pour les stats cibles
    Object.entries(targetStats).forEach(([stat, targetValue]) => {
      const currentValue = item.baseStats[stat] || 0;
      const increase = Math.max(0, targetValue - currentValue);
      const weight = this.getStatWeight(stat);
      puitsUtilise += increase * weight;
    });

    const puitsDisponible = item.puits + puitsLibere;
    const puitsRestant = puitsDisponible - puitsUtilise;

    if (puitsRestant < 0) {
      throw new Error(`Puits insuffisant: ${Math.abs(puitsRestant)} points manquants`);
    }

    // Obtenir les runes recommandées
    const recommendedRunes = await this.getRecommendedRunes(targetStats, statsASupprimer);

    // Calculer le coût total
    let totalCost = 0;
    const itemPrice = await this.dofapiService.getItemPrices(item.id);
    totalCost += itemPrice;

    // Coût des runes (estimation basée sur le puits utilisé)
    const runeCost = this.estimateRuneCost(puitsUtilise, targetStats);
    totalCost += runeCost;

    // Calculer la valeur de revente estimée
    const resaleValue = this.calculateResaleValue(item, targetStats);
    const expectedProfit = Math.max(0, resaleValue - totalCost);
    const profitability = totalCost > 0 ? (expectedProfit / totalCost) * 100 : 0;

    // Générer les scénarios
    const scenarios = this.generateScenarios(item, targetStats, totalCost);

    return {
      item,
      targetStats,
      recommendedRunes,
      totalCost,
      expectedProfit,
      profitability,
      scenarios,
      puitsUtilise,
      puitsDisponible: item.puits
    };
  }

  private getStatWeight(statName: string): number {
    const weights: Record<string, number> = {
      'vitalite': 1,
      'sagesse': 10,
      'force': 10,
      'intelligence': 10,
      'chance': 10,
      'agilite': 10,
      'puissance': 20,
      'dommages': 20,
      'resistance_neutre': 15,
      'resistance_terre': 15,
      'resistance_feu': 15,
      'resistance_eau': 15,
      'resistance_air': 15,
      'pm': 300,
      'pa': 300,
      'portee': 153,
      'invocations': 300,
      'soins': 30,
      'coup_critique': 30,
      'fuite': 15,
      'tacle': 15,
      'esquive_pa': 21,
      'esquive_pm': 21,
      'retrait_pa': 21,
      'retrait_pm': 21
    };

    return weights[statName] || 1;
  }

  private async getRecommendedRunes(
    targetStats: Record<string, number>,
    statsASupprimer: Record<string, number>
  ): Promise<Rune[]> {
    const runes = await this.runesService.getAllRunes();
    const recommendedRunes: Rune[] = [];

    // Runes pour augmenter les stats
    Object.entries(targetStats).forEach(([stat, value]) => {
      const statRunes = runes.filter(rune => 
        rune.effect.toLowerCase().includes(stat.toLowerCase()) ||
        rune.name.toLowerCase().includes(stat.toLowerCase())
      );

      if (statRunes.length > 0) {
        // Prendre la rune la plus appropriée (densité optimale)
        const bestRune = statRunes.sort((a, b) => b.density - a.density)[0];
        recommendedRunes.push(bestRune);
      }
    });

    // Runes pour supprimer les stats
    Object.entries(statsASupprimer).forEach(([stat, value]) => {
      const removalRunes = runes.filter(rune => 
        rune.type === 'ra' && 
        rune.effect.toLowerCase().includes(stat.toLowerCase())
      );

      if (removalRunes.length > 0) {
        recommendedRunes.push(removalRunes[0]);
      }
    });

    return recommendedRunes;
  }

  private estimateRuneCost(puitsUtilise: number, targetStats: Record<string, number>): number {
    // Estimation basée sur le puits et la complexité des stats
    let baseCost = puitsUtilise * 50; // 50 kamas par point de puits

    // Multiplicateur pour les stats exotiques
    const exoticStats = ['pa', 'pm', 'portee', 'invocations'];
    const hasExoticStats = Object.keys(targetStats).some(stat => exoticStats.includes(stat));
    
    if (hasExoticStats) {
      baseCost *= 3; // Les stats exo coûtent 3x plus cher
    }

    // Complexité supplémentaire pour plusieurs stats
    const statsCount = Object.keys(targetStats).length;
    if (statsCount > 3) {
      baseCost *= 1.5;
    }

    return Math.round(baseCost);
  }

  private calculateResaleValue(item: DofusItem, targetStats: Record<string, number>): number {
    // Estimation de la valeur de revente basée sur l'item de base et les améliorations
    const baseValue = item.level * 1000; // Valeur de base selon le niveau

    // Bonus pour chaque stat améliorée
    let statBonus = 0;
    Object.entries(targetStats).forEach(([stat, value]) => {
      const currentValue = item.baseStats[stat] || 0;
      const improvement = Math.max(0, value - currentValue);
      
      // Valeur différente selon le type de stat
      let multiplier = 1000; // Base
      if (['pa', 'pm'].includes(stat)) {
        multiplier = 50000; // PA/PM valent très cher
      } else if (['portee', 'invocations'].includes(stat)) {
        multiplier = 20000;
      } else if (['puissance', 'dommages'].includes(stat)) {
        multiplier = 2000;
      } else if (stat === 'vitalite') {
        multiplier = 500;
      }

      statBonus += improvement * multiplier;
    });

    return baseValue + statBonus;
  }

  private generateScenarios(
    item: DofusItem,
    targetStats: Record<string, number>,
    totalCost: number
  ) {
    // Scénario de Succès Critique (SC) - 5% de chance
    const scValue = this.calculateResaleValue(item, targetStats) * 1.2; // 20% de bonus
    const scProfit = scValue - totalCost;
    
    // Scénario Neutre (SN) - 70% de chance
    const snValue = this.calculateResaleValue(item, targetStats);
    const snProfit = snValue - totalCost;
    
    // Scénario d'Échec Critique (EC) - 25% de chance
    const ecValue = totalCost * 0.3; // Perte de 70% de l'investissement
    const ecProfit = ecValue - totalCost;

    return [
      {
        type: 'SC' as const,
        probability: 0.05,
        result: targetStats,
        value: scProfit
      },
      {
        type: 'SN' as const,
        probability: 0.70,
        result: targetStats,
        value: snProfit
      },
      {
        type: 'EC' as const,
        probability: 0.25,
        result: {},
        value: ecProfit
      }
    ];
  }
}