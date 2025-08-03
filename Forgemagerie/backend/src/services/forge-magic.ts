import { DofusItem, Rune, ForgemagieAnalysis, ForgemagieScenario, ForgemagieConfig } from '../types';

export class ForgemageService {
  private readonly config: ForgemagieConfig = {
    maxOverStats: {
      'vitalite': 40,
      'sagesse': 40,
      'force': 40,
      'intelligence': 40,
      'chance': 40,
      'agilite': 40,
      'puissance': 20,
      'dommages': 20,
      'resistance_neutre': 10,
      'resistance_terre': 10,
      'resistance_feu': 10,
      'resistance_eau': 10,
      'resistance_air': 10,
      'pm': 1,
      'pa': 1,
      'portee': 1,
      'invocations': 1,
      'soins': 10,
      'coup_critique': 10,
      'fuite': 10,
      'tacle': 10,
      'esquive_pa': 10,
      'esquive_pm': 10,
      'retrait_pa': 10,
      'retrait_pm': 10
    },
    runeWeights: {
      'vitalite': 0.2,
      'sagesse': 3,
      'force': 3,
      'intelligence': 3,
      'chance': 3,
      'agilite': 3,
      'puissance': 5,
      'dommages': 5,
      'resistance_neutre': 4,
      'resistance_terre': 4,
      'resistance_feu': 4,
      'resistance_eau': 4,
      'resistance_air': 4,
      'pm': 100,
      'pa': 100,
      'portee': 51,
      'invocations': 100,
      'soins': 10,
      'coup_critique': 10,
      'fuite': 5,
      'tacle': 5,
      'esquive_pa': 7,
      'esquive_pm': 7,
      'retrait_pa': 7,
      'retrait_pm': 7
    },
    baseWeights: {
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
    }
  };

  calculPuits(item: DofusItem, targetStats: Record<string, number>): number {
    let puitsUtilise = 0;
    
    for (const [stat, targetValue] of Object.entries(targetStats)) {
      const currentMax = item.maxStats[stat] || 0;
      const baseMax = item.baseStats[stat] || 0;
      const maxOver = this.config.maxOverStats[stat] || 0;
      
      if (targetValue > currentMax) {
        const overAmount = Math.min(targetValue - currentMax, maxOver);
        puitsUtilise += overAmount * (this.config.baseWeights[stat] || 1);
      }
    }
    
    return puitsUtilise;
  }

  calculPuitsDisponible(item: DofusItem, statsASupprimer: Record<string, number> = {}): number {
    let puitsDisponible = item.puits;
    
    for (const [stat, reduction] of Object.entries(statsASupprimer)) {
      const currentMin = item.baseStats[stat] || 0;
      const actualReduction = Math.min(reduction, currentMin);
      puitsDisponible += actualReduction * (this.config.baseWeights[stat] || 1);
    }
    
    return puitsDisponible;
  }

  selectRunes(
    puitsDisponible: number,
    targetStats: Record<string, number>,
    availableRunes: Rune[]
  ): Rune[] {
    const selectedRunes: Rune[] = [];
    let puitsRestant = puitsDisponible;
    
    const runesByDensity = availableRunes
      .filter(rune => rune.weight <= puitsRestant)
      .sort((a, b) => b.density - a.density);
    
    for (const stat of Object.keys(targetStats)) {
      const targetValue = targetStats[stat];
      let currentValue = 0;
      
      const compatibleRunes = runesByDensity.filter(rune => 
        rune.effect === stat && rune.weight <= puitsRestant
      );
      
      for (const rune of compatibleRunes) {
        while (currentValue < targetValue && puitsRestant >= rune.weight) {
          selectedRunes.push(rune);
          currentValue += this.getRuneEffectValue(rune);
          puitsRestant -= rune.weight;
          
          if (currentValue >= targetValue) break;
        }
        
        if (currentValue >= targetValue) break;
      }
    }
    
    return selectedRunes;
  }

  private getRuneEffectValue(rune: Rune): number {
    switch (rune.type) {
      case 'pa':
        return rune.name.includes('Pa') ? 1 : 0;
      case 'ra':
        return parseInt(rune.name.match(/\d+/)?.[0] || '1');
      case 'ga':
        return parseInt(rune.name.match(/\d+/)?.[0] || '1');
      case 'exo':
        return parseInt(rune.name.match(/\d+/)?.[0] || '1');
      default:
        return 1;
    }
  }

  simulateFM(analysis: Omit<ForgemagieAnalysis, 'scenarios'>): ForgemagieScenario[] {
    const baseValue = this.estimateItemValue(analysis.item, analysis.targetStats);
    const itemCost = analysis.item.baseStats.prix || 10000;
    
    const scenarios: ForgemagieScenario[] = [
      {
        type: 'SC',
        probability: 0.15,
        result: analysis.targetStats,
        value: baseValue * 1.3
      },
      {
        type: 'SN',
        probability: 0.70,
        result: this.applyNeutralResult(analysis.targetStats),
        value: baseValue
      },
      {
        type: 'EC',
        probability: 0.15,
        result: this.applyFailureResult(analysis.targetStats),
        value: itemCost * 0.7
      }
    ];
    
    return scenarios;
  }

  private applyNeutralResult(targetStats: Record<string, number>): Record<string, number> {
    const result = { ...targetStats };
    
    for (const stat of Object.keys(result)) {
      result[stat] = Math.round(result[stat] * 0.9);
    }
    
    return result;
  }

  private applyFailureResult(targetStats: Record<string, number>): Record<string, number> {
    const result = { ...targetStats };
    
    for (const stat of Object.keys(result)) {
      result[stat] = Math.round(result[stat] * 0.6);
    }
    
    return result;
  }

  private estimateItemValue(item: DofusItem, finalStats: Record<string, number>): number {
    let value = item.baseStats.prix || 10000;
    
    for (const [stat, statValue] of Object.entries(finalStats)) {
      const baseValue = item.baseStats[stat] || 0;
      const improvement = statValue - baseValue;
      
      if (improvement > 0) {
        const statMultiplier = this.getStatValueMultiplier(stat);
        value += improvement * statMultiplier;
      }
    }
    
    return value;
  }

  private getStatValueMultiplier(stat: string): number {
    const multipliers: Record<string, number> = {
      'pa': 50000,
      'pm': 30000,
      'portee': 15000,
      'invocations': 10000,
      'puissance': 500,
      'dommages': 500,
      'vitalite': 15,
      'sagesse': 100,
      'force': 100,
      'intelligence': 100,
      'chance': 100,
      'agilite': 100,
      'coup_critique': 200,
      'soins': 300,
      'esquive_pa': 300,
      'esquive_pm': 300,
      'retrait_pa': 300,
      'retrait_pm': 300,
      'resistance_neutre': 200,
      'resistance_terre': 200,
      'resistance_feu': 200,
      'resistance_eau': 200,
      'resistance_air': 200
    };
    
    return multipliers[stat] || 50;
  }

  analyzeItem(
    item: DofusItem,
    targetStats: Record<string, number>,
    availableRunes: Rune[],
    statsASupprimer: Record<string, number> = {}
  ): ForgemagieAnalysis {
    const puitsDisponible = this.calculPuitsDisponible(item, statsASupprimer);
    const puitsUtilise = this.calculPuits(item, targetStats);
    
    if (puitsUtilise > puitsDisponible) {
      throw new Error(`Puits insuffisant: ${puitsUtilise} requis, ${puitsDisponible} disponible`);
    }
    
    const recommendedRunes = this.selectRunes(puitsUtilise, targetStats, availableRunes);
    const totalCost = recommendedRunes.reduce((sum, rune) => sum + rune.price, 0);
    
    const baseAnalysis = {
      item,
      targetStats,
      recommendedRunes,
      totalCost,
      expectedProfit: 0,
      profitability: 0,
      puitsUtilise,
      puitsDisponible
    };
    
    const scenarios = this.simulateFM(baseAnalysis);
    const expectedValue = scenarios.reduce((sum, scenario) => 
      sum + (scenario.value * scenario.probability), 0
    );
    
    const itemCost = item.baseStats.prix || 10000;
    const expectedProfit = expectedValue - totalCost - itemCost;
    const profitability = (expectedProfit / (totalCost + itemCost)) * 100;
    
    return {
      ...baseAnalysis,
      scenarios,
      expectedProfit,
      profitability
    };
  }
}