import { ForgemageService } from '../services/forge-magic';
import { DofusItem, Rune } from '../types';

describe('ForgemageService', () => {
  let service: ForgemageService;
  let mockItem: DofusItem;
  let mockRunes: Rune[];

  beforeEach(() => {
    service = new ForgemageService();
    
    mockItem = {
      id: 1,
      name: 'Gelano Test',
      type: 'Bottes',
      level: 100,
      baseStats: {
        vitalite: 200,
        agilite: 30,
        prix: 50000
      },
      maxStats: {
        vitalite: 300,
        agilite: 50
      },
      weight: 1000,
      puits: 100
    };

    mockRunes = [
      {
        id: 1,
        name: 'Rune Vi',
        effect: 'vitalite',
        weight: 1,
        density: 1,
        type: 'ra',
        price: 50
      },
      {
        id: 2,
        name: 'Rune Agi',
        effect: 'agilite',
        weight: 3,
        density: 0.33,
        type: 'ra',
        price: 150
      },
      {
        id: 3,
        name: 'Rune Pa',
        effect: 'pa',
        weight: 100,
        density: 0.01,
        type: 'pa',
        price: 150000
      }
    ];
  });

  describe('calculPuits', () => {
    it('should calculate puits correctly for over max stats', () => {
      const targetStats = {
        vitalite: 320, // +20 over max (300)
        agilite: 60    // +10 over max (50)
      };

      const puits = service.calculPuits(mockItem, targetStats);
      
      expect(puits).toBe(50); // 20 * 1 (vi weight) + 10 * 10 (agi weight) = 120, but limited by maxOver
    });

    it('should return 0 for stats within max range', () => {
      const targetStats = {
        vitalite: 280, // within max (300)
        agilite: 45    // within max (50)
      };

      const puits = service.calculPuits(mockItem, targetStats);
      
      expect(puits).toBe(0);
    });
  });

  describe('calculPuitsDisponible', () => {
    it('should calculate available puits correctly', () => {
      const puitsDisponible = service.calculPuitsDisponible(mockItem);
      
      expect(puitsDisponible).toBe(100); // base puits
    });

    it('should add puits when removing stats', () => {
      const statsASupprimer = {
        vitalite: 50 // remove 50 vita
      };

      const puitsDisponible = service.calculPuitsDisponible(mockItem, statsASupprimer);
      
      expect(puitsDisponible).toBe(150); // 100 + (50 * 1)
    });
  });

  describe('selectRunes', () => {
    it('should select appropriate runes for target stats', () => {
      const targetStats = {
        vitalite: 50 // need 50 over
      };

      const selectedRunes = service.selectRunes(100, targetStats, mockRunes);
      
      expect(selectedRunes).toHaveLength(50); // 50 Vi runes
      expect(selectedRunes.every(rune => rune.effect === 'vitalite')).toBe(true);
    });

    it('should respect puits limit', () => {
      const targetStats = {
        vitalite: 200 // would need 200 Vi runes (200 poids)
      };

      const selectedRunes = service.selectRunes(50, targetStats, mockRunes); // only 50 puits available
      
      expect(selectedRunes).toHaveLength(50); // limited by available puits
    });
  });

  describe('analyzeItem', () => {
    it('should perform complete analysis', () => {
      const targetStats = {
        vitalite: 320 // +20 over max
      };

      const analysis = service.analyzeItem(mockItem, targetStats, mockRunes);
      
      expect(analysis.item).toBe(mockItem);
      expect(analysis.targetStats).toEqual(targetStats);
      expect(analysis.recommendedRunes).toBeDefined();
      expect(analysis.totalCost).toBeGreaterThan(0);
      expect(analysis.scenarios).toHaveLength(3); // SC, SN, EC
      expect(analysis.puitsUtilise).toBeGreaterThan(0);
      expect(analysis.puitsDisponible).toBe(100);
    });

    it('should throw error when insufficient puits', () => {
      const targetStats = {
        vitalite: 400 // way over max, requires too much puits
      };

      expect(() => {
        service.analyzeItem(mockItem, targetStats, mockRunes);
      }).toThrow('Puits insuffisant');
    });
  });

  describe('simulateFM', () => {
    it('should generate three scenarios with correct probabilities', () => {
      const baseAnalysis = {
        item: mockItem,
        targetStats: { vitalite: 320 },
        recommendedRunes: [mockRunes[0]],
        totalCost: 1000,
        expectedProfit: 0,
        profitability: 0,
        puitsUtilise: 20,
        puitsDisponible: 100
      };

      const scenarios = service.simulateFM(baseAnalysis);
      
      expect(scenarios).toHaveLength(3);
      expect(scenarios.find(s => s.type === 'SC')?.probability).toBe(0.15);
      expect(scenarios.find(s => s.type === 'SN')?.probability).toBe(0.70);
      expect(scenarios.find(s => s.type === 'EC')?.probability).toBe(0.15);
      
      const totalProbability = scenarios.reduce((sum, s) => sum + s.probability, 0);
      expect(totalProbability).toBe(1.0);
    });
  });
});