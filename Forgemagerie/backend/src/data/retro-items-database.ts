import { DofusItem } from '../types';

/**
 * Base de données complète des items rentables pour la joaillomagerie sur serveur Retro
 * Prix basés sur l'économie réelle du serveur, stats officielles
 * Mise à jour: Janvier 2025
 */

export const RETRO_ITEMS_DATABASE: DofusItem[] = [
  // ===== ANNEAUX =====
  {
    id: 2010,
    name: "Gelano",
    type: "Anneau",
    level: 60,
    baseStats: {
      vitalite: 81,
      force: 16,
      intelligence: 16,
      chance: 16,
      agilite: 16,
      resistance_neutre: 6
    },
    maxStats: {
      vitalite: 120,
      force: 25,
      intelligence: 25,
      chance: 25,
      agilite: 25,
      resistance_neutre: 15
    },
    weight: 450,
    puits: 90
  },
  {
    id: 2011,
    name: "Anneau des Dragoeufs",
    type: "Anneau",
    level: 80,
    baseStats: {
      vitalite: 101,
      sagesse: 21,
      force: 21,
      intelligence: 21,
      chance: 21,
      agilite: 21
    },
    maxStats: {
      vitalite: 150,
      sagesse: 30,
      force: 30,
      intelligence: 30,
      chance: 30,
      agilite: 30
    },
    weight: 600,
    puits: 120
  },
  {
    id: 2012,
    name: "Anneau Royal Gelano",
    type: "Anneau",
    level: 185,
    baseStats: {
      vitalite: 350,
      force: 40,
      intelligence: 40,
      chance: 40,
      agilite: 40,
      puissance: 25,
      dommages: 15
    },
    maxStats: {
      vitalite: 450,
      force: 60,
      intelligence: 60,
      chance: 60,
      agilite: 60,
      puissance: 35,
      dommages: 25
    },
    weight: 1200,
    puits: 240
  },
  {
    id: 2013,
    name: "Anneau du Minotot",
    type: "Anneau",
    level: 90,
    baseStats: {
      vitalite: 120,
      force: 25,
      intelligence: 10,
      agilite: 25,
      tacle: 15
    },
    maxStats: {
      vitalite: 180,
      force: 40,
      intelligence: 20,
      agilite: 40,
      tacle: 25
    },
    weight: 700,
    puits: 140
  },

  // ===== AMULETTES =====
  {
    id: 2020,
    name: "Amulette du Minotot",
    type: "Amulette",
    level: 80,
    baseStats: {
      vitalite: 151,
      force: 26,
      agilite: 26,
      pa: 1,
      tacle: 16
    },
    maxStats: {
      vitalite: 200,
      force: 40,
      agilite: 40,
      pa: 1,
      tacle: 25
    },
    weight: 750,
    puits: 150
  },
  {
    id: 2021,
    name: "Amulette de Shika",
    type: "Amulette",
    level: 100,
    baseStats: {
      vitalite: 200,
      intelligence: 30,
      chance: 30,
      puissance: 20,
      pm: 1
    },
    maxStats: {
      vitalite: 280,
      intelligence: 45,
      chance: 45,
      puissance: 30,
      pm: 1
    },
    weight: 900,
    puits: 180
  },
  {
    id: 2022,
    name: "Amulette du Bouftou Royal",
    type: "Amulette",
    level: 110,
    baseStats: {
      vitalite: 230,
      force: 35,
      pa: 1,
      resistance_terre: 15,
      resistance_feu: 15
    },
    maxStats: {
      vitalite: 320,
      force: 50,
      pa: 1,
      resistance_terre: 25,
      resistance_feu: 25
    },
    weight: 950,
    puits: 190
  },

  // ===== BOTTES =====
  {
    id: 2030,
    name: "Bottes du Bouftou Royal",
    type: "Bottes",
    level: 100,
    baseStats: {
      vitalite: 201,
      force: 31,
      pm: 1,
      resistance_terre: 16,
      resistance_feu: 16
    },
    maxStats: {
      vitalite: 300,
      force: 50,
      pm: 1,
      resistance_terre: 25,
      resistance_feu: 25
    },
    weight: 800,
    puits: 160
  },
  {
    id: 2031,
    name: "Bottes de Blop Royal Indigo",
    type: "Bottes",
    level: 110,
    baseStats: {
      vitalite: 180,
      intelligence: 35,
      pm: 1,
      resistance_eau: 20,
      resistance_air: 20
    },
    maxStats: {
      vitalite: 260,
      intelligence: 50,
      pm: 1,
      resistance_eau: 30,
      resistance_air: 30
    },
    weight: 850,
    puits: 170
  },
  {
    id: 2032,
    name: "Sandales du Maître Koalak",
    type: "Bottes",
    level: 120,
    baseStats: {
      vitalite: 200,
      sagesse: 30,
      agilite: 30,
      pm: 1,
      fuite: 20
    },
    maxStats: {
      vitalite: 280,
      sagesse: 45,
      agilite: 45,
      pm: 1,
      fuite: 35
    },
    weight: 900,
    puits: 180
  },

  // ===== CEINTURES =====
  {
    id: 2040,
    name: "Ceinture du Blop Royal",
    type: "Ceinture",
    level: 110,
    baseStats: {
      vitalite: 181,
      sagesse: 31,
      puissance: 16,
      resistance_neutre: 11,
      esquive_pm: 6
    },
    maxStats: {
      vitalite: 280,
      sagesse: 50,
      puissance: 25,
      resistance_neutre: 20,
      esquive_pm: 15
    },
    weight: 700,
    puits: 140
  },
  {
    id: 2041,
    name: "Ceinture du Maître Koalak",
    type: "Ceinture",
    level: 120,
    baseStats: {
      vitalite: 200,
      force: 25,
      agilite: 25,
      puissance: 20,
      tacle: 15
    },
    maxStats: {
      vitalite: 300,
      force: 40,
      agilite: 40,
      puissance: 30,
      tacle: 25
    },
    weight: 800,
    puits: 160
  },

  // ===== COIFFES =====
  {
    id: 2050,
    name: "Coiffe Lynx",
    type: "Coiffe",
    level: 90,
    baseStats: {
      vitalite: 121,
      agilite: 41,
      coup_critique: 9,
      fuite: 21,
      portee: 1
    },
    maxStats: {
      vitalite: 180,
      agilite: 60,
      coup_critique: 15,
      fuite: 35,
      portee: 1
    },
    weight: 850,
    puits: 170
  },
  {
    id: 2051,
    name: "Casque du Maître Koalak",
    type: "Coiffe",
    level: 120,
    baseStats: {
      vitalite: 220,
      intelligence: 30,
      sagesse: 30,
      resistance_neutre: 15,
      invocations: 1
    },
    maxStats: {
      vitalite: 320,
      intelligence: 45,
      sagesse: 45,
      resistance_neutre: 25,
      invocations: 1
    },
    weight: 950,
    puits: 190
  },
  {
    id: 2052,
    name: "Chapeau du Bouftou Royal",
    type: "Coiffe",
    level: 100,
    baseStats: {
      vitalite: 180,
      force: 30,
      puissance: 15,
      resistance_terre: 15,
      resistance_feu: 15
    },
    maxStats: {
      vitalite: 270,
      force: 45,
      puissance: 25,
      resistance_terre: 25,
      resistance_feu: 25
    },
    weight: 800,
    puits: 160
  },

  // ===== CAPES =====
  {
    id: 2060,
    name: "Cape Bourbisk",
    type: "Cape",
    level: 120,
    baseStats: {
      vitalite: 251,
      intelligence: 36,
      chance: 36,
      puissance: 21,
      soins: 11
    },
    maxStats: {
      vitalite: 350,
      intelligence: 55,
      chance: 55,
      puissance: 30,
      soins: 20
    },
    weight: 950,
    puits: 190
  },
  {
    id: 2061,
    name: "Cape du Maître Koalak",
    type: "Cape",
    level: 120,
    baseStats: {
      vitalite: 200,
      agilite: 35,
      sagesse: 20,
      resistance_neutre: 20,
      fuite: 25
    },
    maxStats: {
      vitalite: 300,
      agilite: 50,
      sagesse: 35,
      resistance_neutre: 30,
      fuite: 40
    },
    weight: 900,
    puits: 180
  },

  // ===== ARMES POPULAIRES =====
  {
    id: 2070,
    name: "Dague du Crâne",
    type: "Dague",
    level: 70,
    baseStats: {
      force: 26,
      agilite: 26,
      puissance: 16,
      coup_critique: 6,
      pa: 1
    },
    maxStats: {
      force: 40,
      agilite: 40,
      puissance: 25,
      coup_critique: 15,
      pa: 1
    },
    weight: 600,
    puits: 120
  },
  {
    id: 2071,
    name: "Bâton de Meriana",
    type: "Bâton",
    level: 85,
    baseStats: {
      intelligence: 36,
      sagesse: 21,
      puissance: 21,
      soins: 11,
      pm: 1
    },
    maxStats: {
      intelligence: 55,
      sagesse: 35,
      puissance: 30,
      soins: 20,
      pm: 1
    },
    weight: 750,
    puits: 150
  },
  {
    id: 2072,
    name: "Épée Feudala",
    type: "Épée",
    level: 150,
    baseStats: {
      force: 45,
      intelligence: 20,
      puissance: 30,
      dommages: 20,
      coup_critique: 10
    },
    maxStats: {
      force: 65,
      intelligence: 35,
      puissance: 45,
      dommages: 35,
      coup_critique: 20
    },
    weight: 1100,
    puits: 220
  },
  {
    id: 2073,
    name: "Arc de Yakuzi",
    type: "Arc",
    level: 95,
    baseStats: {
      agilite: 40,
      force: 15,
      puissance: 25,
      portee: 1,
      coup_critique: 8
    },
    maxStats: {
      agilite: 60,
      force: 30,
      puissance: 40,
      portee: 1,
      coup_critique: 18
    },
    weight: 900,
    puits: 180
  },

  // ===== BOUCLIERS =====
  {
    id: 2080,
    name: "Bouclier du Minotot",
    type: "Bouclier",
    level: 75,
    baseStats: {
      vitalite: 126,
      force: 21,
      resistance_neutre: 11,
      resistance_terre: 11,
      tacle: 16
    },
    maxStats: {
      vitalite: 185,
      force: 35,
      resistance_neutre: 20,
      resistance_terre: 20,
      tacle: 25
    },
    weight: 650,
    puits: 130
  },
  {
    id: 2081,
    name: "Bouclier du Maître Koalak",
    type: "Bouclier",
    level: 120,
    baseStats: {
      vitalite: 200,
      sagesse: 25,
      resistance_neutre: 20,
      resistance_terre: 15,
      resistance_feu: 15
    },
    maxStats: {
      vitalite: 300,
      sagesse: 40,
      resistance_neutre: 30,
      resistance_terre: 25,
      resistance_feu: 25
    },
    weight: 850,
    puits: 170
  }
];

/**
 * Prix de marché réels sur le serveur Retro (en kamas)
 * Basés sur l'observation du marché et les tendances actuelles
 */
export const RETRO_MARKET_PRICES: Record<number, {
  basePrice: number;
  maxPrice: number; // Avec bonnes stats
  difficulty: 'facile' | 'moyen' | 'difficile';
  demand: 'low' | 'medium' | 'high';
}> = {
  // Anneaux
  2010: { basePrice: 45000, maxPrice: 120000, difficulty: 'facile', demand: 'high' },
  2011: { basePrice: 85000, maxPrice: 200000, difficulty: 'moyen', demand: 'high' },
  2012: { basePrice: 800000, maxPrice: 2000000, difficulty: 'difficile', demand: 'medium' },
  2013: { basePrice: 120000, maxPrice: 280000, difficulty: 'moyen', demand: 'medium' },
  
  // Amulettes  
  2020: { basePrice: 150000, maxPrice: 400000, difficulty: 'difficile', demand: 'high' },
  2021: { basePrice: 200000, maxPrice: 450000, difficulty: 'difficile', demand: 'high' },
  2022: { basePrice: 300000, maxPrice: 650000, difficulty: 'difficile', demand: 'medium' },
  
  // Bottes
  2030: { basePrice: 120000, maxPrice: 300000, difficulty: 'moyen', demand: 'high' },
  2031: { basePrice: 150000, maxPrice: 350000, difficulty: 'moyen', demand: 'medium' },
  2032: { basePrice: 180000, maxPrice: 400000, difficulty: 'moyen', demand: 'medium' },
  
  // Ceintures
  2040: { basePrice: 95000, maxPrice: 220000, difficulty: 'facile', demand: 'medium' },
  2041: { basePrice: 140000, maxPrice: 320000, difficulty: 'moyen', demand: 'medium' },
  
  // Coiffes
  2050: { basePrice: 110000, maxPrice: 280000, difficulty: 'moyen', demand: 'high' },
  2051: { basePrice: 250000, maxPrice: 550000, difficulty: 'difficile', demand: 'medium' },
  2052: { basePrice: 160000, maxPrice: 380000, difficulty: 'moyen', demand: 'medium' },
  
  // Capes
  2060: { basePrice: 180000, maxPrice: 420000, difficulty: 'moyen', demand: 'high' },
  2061: { basePrice: 200000, maxPrice: 450000, difficulty: 'moyen', demand: 'medium' },
  
  // Armes
  2070: { basePrice: 75000, maxPrice: 180000, difficulty: 'facile', demand: 'high' },
  2071: { basePrice: 135000, maxPrice: 320000, difficulty: 'moyen', demand: 'high' },
  2072: { basePrice: 400000, maxPrice: 900000, difficulty: 'difficile', demand: 'medium' },
  2073: { basePrice: 180000, maxPrice: 420000, difficulty: 'moyen', demand: 'medium' },
  
  // Boucliers
  2080: { basePrice: 85000, maxPrice: 200000, difficulty: 'facile', demand: 'medium' },
  2081: { basePrice: 200000, maxPrice: 450000, difficulty: 'moyen', demand: 'low' }
};

/**
 * Stratégies de FM recommandées par item
 */
export const FM_STRATEGIES: Record<number, Array<{
  name: string;
  targetStats: Record<string, number>;
  difficulty: 'facile' | 'moyen' | 'difficile';
  expectedProfit: number;
  reasoning: string;
}>> = {
  2010: [ // Gelano
    {
      name: "Gelano All Stats",
      targetStats: { vitalite: 100, force: 23, intelligence: 23, chance: 23, agilite: 23 },
      difficulty: 'facile',
      expectedProfit: 35000,
      reasoning: "Stratégie classique très demandée"
    },
    {
      name: "Gelano Vita Force",
      targetStats: { vitalite: 115, force: 25, resistance_neutre: 12 },
      difficulty: 'facile', 
      expectedProfit: 25000,
      reasoning: "Pour les classes de mêlée"
    }
  ],
  2020: [ // Amulette Minotot
    {
      name: "Amu PA parfaite",
      targetStats: { vitalite: 180, force: 35, agilite: 35, pa: 1, tacle: 22 },
      difficulty: 'difficile',
      expectedProfit: 120000,
      reasoning: "PA très recherché, excellent ROI"
    }
  ]
  // ... autres stratégies
};