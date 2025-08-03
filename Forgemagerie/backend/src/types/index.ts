export interface DofusItem {
  id: number;
  name: string;
  type: string;
  level: number;
  baseStats: Record<string, number>;
  maxStats: Record<string, number>;
  weight: number;
  puits: number;
}

export interface Rune {
  id: number;
  name: string;
  effect: string;
  weight: number;
  density: number;
  type: 'pa' | 'ra' | 'ga' | 'exo';
  price: number;
}

export interface ForgemagieScenario {
  type: 'SC' | 'SN' | 'EC';
  probability: number;
  result: Record<string, number>;
  value: number;
}

export interface ForgemagieAnalysis {
  item: DofusItem;
  targetStats: Record<string, number>;
  recommendedRunes: Rune[];
  totalCost: number;
  expectedProfit: number;
  profitability: number;
  scenarios: ForgemagieScenario[];
  puitsUtilise: number;
  puitsDisponible: number;
}

export interface ItemPrice {
  itemId: number;
  price: number;
  server: string;
  date: Date;
}

export interface RunePrice {
  runeId: number;
  price: number;
  server: string;
  date: Date;
}

export interface DofapiItem {
  id: number;
  name: {
    fr: string;
    en: string;
  };
  type: {
    name: {
      fr: string;
      en: string;
    };
  };
  level: number;
  statistics: Array<{
    characteristic: {
      name: {
        fr: string;
        en: string;
      };
    };
    from: number;
    to?: number;
  }>;
}

export interface ForgemagieConfig {
  maxOverStats: Record<string, number>;
  runeWeights: Record<string, number>;
  baseWeights: Record<string, number>;
}