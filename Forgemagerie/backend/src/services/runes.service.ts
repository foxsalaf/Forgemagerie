import { Rune } from '../types';

export class RunesService {
  private readonly runes: Rune[] = [
    { id: 1, name: 'Rune Pa', effect: 'pa', weight: 100, density: 0.01, type: 'pa', price: 150000 },
    { id: 2, name: 'Rune Pm', effect: 'pm', weight: 100, density: 0.01, type: 'pa', price: 120000 },
    { id: 3, name: 'Rune Po', effect: 'portee', weight: 51, density: 0.02, type: 'pa', price: 80000 },
    
    { id: 10, name: 'Rune Vi', effect: 'vitalite', weight: 1, density: 1, type: 'ra', price: 50 },
    { id: 11, name: 'Rune Age', effect: 'sagesse', weight: 3, density: 0.33, type: 'ra', price: 150 },
    { id: 12, name: 'Rune Fo', effect: 'force', weight: 3, density: 0.33, type: 'ra', price: 150 },
    { id: 13, name: 'Rune Ine', effect: 'intelligence', weight: 3, density: 0.33, type: 'ra', price: 150 },
    { id: 14, name: 'Rune Cha', effect: 'chance', weight: 3, density: 0.33, type: 'ra', price: 150 },
    { id: 15, name: 'Rune Age', effect: 'agilite', weight: 3, density: 0.33, type: 'ra', price: 150 },
    { id: 16, name: 'Rune Puissance', effect: 'puissance', weight: 5, density: 0.2, type: 'ra', price: 800 },
    { id: 17, name: 'Rune Do', effect: 'dommages', weight: 5, density: 0.2, type: 'ra', price: 800 },
    { id: 18, name: 'Rune Re Neu', effect: 'resistance_neutre', weight: 4, density: 0.25, type: 'ra', price: 400 },
    { id: 19, name: 'Rune Re Ter', effect: 'resistance_terre', weight: 4, density: 0.25, type: 'ra', price: 400 },
    { id: 20, name: 'Rune Re Feu', effect: 'resistance_feu', weight: 4, density: 0.25, type: 'ra', price: 400 },
    { id: 21, name: 'Rune Re Eau', effect: 'resistance_eau', weight: 4, density: 0.25, type: 'ra', price: 400 },
    { id: 22, name: 'Rune Re Air', effect: 'resistance_air', weight: 4, density: 0.25, type: 'ra', price: 400 },
    { id: 23, name: 'Rune So', effect: 'soins', weight: 10, density: 0.1, type: 'ra', price: 1000 },
    { id: 24, name: 'Rune Cri', effect: 'coup_critique', weight: 10, density: 0.1, type: 'ra', price: 1200 },
    { id: 25, name: 'Rune Fui', effect: 'fuite', weight: 5, density: 0.2, type: 'ra', price: 500 },
    { id: 26, name: 'Rune Tac', effect: 'tacle', weight: 5, density: 0.2, type: 'ra', price: 500 },
    { id: 27, name: 'Rune Esquive PA', effect: 'esquive_pa', weight: 7, density: 0.14, type: 'ra', price: 800 },
    { id: 28, name: 'Rune Esquive PM', effect: 'esquive_pm', weight: 7, density: 0.14, type: 'ra', price: 800 },
    { id: 29, name: 'Rune Retrait PA', effect: 'retrait_pa', weight: 7, density: 0.14, type: 'ra', price: 800 },
    { id: 30, name: 'Rune Retrait PM', effect: 'retrait_pm', weight: 7, density: 0.14, type: 'ra', price: 800 },

    { id: 50, name: 'Grande Rune Vi', effect: 'vitalite', weight: 3, density: 3.33, type: 'ga', price: 200 },
    { id: 51, name: 'Grande Rune Age', effect: 'sagesse', weight: 10, density: 1, type: 'ga', price: 1500 },
    { id: 52, name: 'Grande Rune Fo', effect: 'force', weight: 10, density: 1, type: 'ga', price: 1500 },
    { id: 53, name: 'Grande Rune Ine', effect: 'intelligence', weight: 10, density: 1, type: 'ga', price: 1500 },
    { id: 54, name: 'Grande Rune Cha', effect: 'chance', weight: 10, density: 1, type: 'ga', price: 1500 },
    { id: 55, name: 'Grande Rune Agi', effect: 'agilite', weight: 10, density: 1, type: 'ga', price: 1500 },
    { id: 56, name: 'Grande Rune Puissance', effect: 'puissance', weight: 20, density: 0.5, type: 'ga', price: 8000 },
    { id: 57, name: 'Grande Rune Do', effect: 'dommages', weight: 20, density: 0.5, type: 'ga', price: 8000 },

    { id: 100, name: 'Rune Exo Pa', effect: 'pa', weight: 300, density: 0.003, type: 'exo', price: 2000000 },
    { id: 101, name: 'Rune Exo Pm', effect: 'pm', weight: 300, density: 0.003, type: 'exo', price: 1500000 },
    { id: 102, name: 'Rune Exo Po', effect: 'portee', weight: 153, density: 0.007, type: 'exo', price: 800000 },
    { id: 103, name: 'Rune Exo Invo', effect: 'invocations', weight: 300, density: 0.003, type: 'exo', price: 1000000 },
    { id: 104, name: 'Rune Exo Fo', effect: 'force', weight: 30, density: 0.033, type: 'exo', price: 50000 },
    { id: 105, name: 'Rune Exo Ine', effect: 'intelligence', weight: 30, density: 0.033, type: 'exo', price: 50000 },
    { id: 106, name: 'Rune Exo Cha', effect: 'chance', weight: 30, density: 0.033, type: 'exo', price: 50000 },
    { id: 107, name: 'Rune Exo Agi', effect: 'agilite', weight: 30, density: 0.033, type: 'exo', price: 50000 },
    { id: 108, name: 'Rune Exo Age', effect: 'sagesse', weight: 30, density: 0.033, type: 'exo', price: 60000 },
    { id: 109, name: 'Rune Exo Vi', effect: 'vitalite', weight: 3, density: 0.33, type: 'exo', price: 5000 }
  ];

  getAllRunes(): Rune[] {
    return this.runes.map(rune => ({
      ...rune,
      price: this.getRunePrice(rune.id)
    }));
  }

  getRunesByType(type: string): Rune[] {
    return this.runes
      .filter(rune => rune.type === type)
      .map(rune => ({
        ...rune,
        price: this.getRunePrice(rune.id)
      }));
  }

  getRunesByEffect(effect: string): Rune[] {
    return this.runes
      .filter(rune => rune.effect === effect)
      .map(rune => ({
        ...rune,
        price: this.getRunePrice(rune.id)
      }));
  }

  getRuneById(id: number): Rune | null {
    const rune = this.runes.find(r => r.id === id);
    if (!rune) return null;

    return {
      ...rune,
      price: this.getRunePrice(rune.id)
    };
  }

  private getRunePrice(runeId: number): number {
    const baseRune = this.runes.find(r => r.id === runeId);
    if (!baseRune) return 1000;

    const variation = (Math.random() - 0.5) * 0.2;
    return Math.round(baseRune.price * (1 + variation));
  }

  async updateRunePrices(): Promise<void> {
    console.log('Mise à jour des prix des runes...');
  }

  getOptimalRuneCombination(
    effect: string,
    targetAmount: number,
    maxWeight: number
  ): Rune[] {
    const compatibleRunes = this.getRunesByEffect(effect)
      .filter(rune => rune.weight <= maxWeight)
      .sort((a, b) => b.density - a.density);

    const combination: Rune[] = [];
    let remainingAmount = targetAmount;
    let remainingWeight = maxWeight;

    for (const rune of compatibleRunes) {
      const runeValue = this.getRuneEffectValue(rune);
      const maxUses = Math.min(
        Math.floor(remainingAmount / runeValue),
        Math.floor(remainingWeight / rune.weight)
      );

      for (let i = 0; i < maxUses; i++) {
        combination.push(rune);
        remainingAmount -= runeValue;
        remainingWeight -= rune.weight;

        if (remainingAmount <= 0) break;
      }

      if (remainingAmount <= 0) break;
    }

    return combination;
  }

  private getRuneEffectValue(rune: Rune): number {
    switch (rune.type) {
      case 'pa':
        return rune.name.includes('Pa') ? 1 : 0;
      case 'ra':
        if (rune.effect === 'vitalite') return 1;
        return 1;
      case 'ga':
        if (rune.effect === 'vitalite') return 10;
        return 10;
      case 'exo':
        if (rune.effect === 'vitalite') return 1;
        return 1;
      default:
        return 1;
    }
  }
}