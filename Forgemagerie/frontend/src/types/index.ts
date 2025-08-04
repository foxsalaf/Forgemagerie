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

export interface SearchResult {
  id: number;
  name: string;
  type: string;
  level: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export interface AssistantRecommendation {
  item: DofusItem;
  analysis: ForgemagieAnalysis;
  profitMargin: number;
  investmentReturn: number;
  difficulty: 'facile' | 'moyen' | 'difficile';
  estimatedTime: number;
  reasoning: string;
}

export interface AssistantRequest {
  server: string;
  budget: number;
  preferredStats: string[];
  riskTolerance: 'conservateur' | 'modere' | 'agressif';
  minProfitMargin?: number;
  maxItemLevel?: number;
  excludedTypes?: string[];
}

export interface AssistantResponse {
  recommendations: AssistantRecommendation[];
  totalBudgetUsed: number;
  estimatedTotalProfit: number;
  marketAnalysis: {
    bestOpportunities: string[];
    marketTrends: string[];
    warnings: string[];
  };
}

export interface MarketInsights {
  hotItems: Array<{
    type: string;
    demand: 'low' | 'medium' | 'high';
    reason: string;
  }>;
  profitableStats: Array<{
    stat: string;
    avgProfit: number;
    difficulty: 'facile' | 'moyen' | 'difficile';
  }>;
  budgetRecommendations: {
    beginner: { min: number; recommended: number; description: string };
    intermediate: { min: number; recommended: number; description: string };
    advanced: { min: number; recommended: number; description: string };
  };
  serverSpecific: {
    server: string;
    marketActivity: string;
    bestTimeToSell: string;
    competitionLevel: string;
  };
}