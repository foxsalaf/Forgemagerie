import { DofusItem } from '../types';
import { RETRO_ITEMS_DATABASE, RETRO_MARKET_PRICES, FM_STRATEGIES } from '../data/retro-items-database';

export class RetroDatabaseService {
  
  /**
   * Recherche d'items par nom ou type
   */
  searchItems(query: string): DofusItem[] {
    const searchTerm = query.toLowerCase().trim();
    
    return RETRO_ITEMS_DATABASE.filter(item => 
      item.name.toLowerCase().includes(searchTerm) ||
      item.type.toLowerCase().includes(searchTerm) ||
      searchTerm === '' // Si recherche vide, retourner tous les items
    );
  }

  /**
   * Obtenir un item par ID
   */
  getItemById(id: number): DofusItem | null {
    return RETRO_ITEMS_DATABASE.find(item => item.id === id) || null;
  }

  /**
   * Obtenir le prix d'un item sur le marché
   */
  getItemPrice(itemId: number): number {
    const priceInfo = RETRO_MARKET_PRICES[itemId];
    if (!priceInfo) return 50000; // Prix par défaut
    
    // Variation aléatoire entre prix de base et prix moyen du marché
    const variation = Math.random() * 0.3; // ±15%
    const avgPrice = (priceInfo.basePrice + priceInfo.maxPrice) / 2;
    return Math.round(avgPrice * (1 + (variation - 0.15)));
  }

  /**
   * Obtenir les informations de marché d'un item
   */
  getMarketInfo(itemId: number) {
    return RETRO_MARKET_PRICES[itemId] || {
      basePrice: 50000,
      maxPrice: 100000,
      difficulty: 'moyen' as const,
      demand: 'medium' as const
    };
  }

  /**
   * Obtenir les stratégies de FM pour un item
   */
  getFMStrategies(itemId: number) {
    return FM_STRATEGIES[itemId] || [];
  }

  /**
   * Obtenir les items par type
   */
  getItemsByType(type: string): DofusItem[] {
    return RETRO_ITEMS_DATABASE.filter(item => 
      item.type.toLowerCase() === type.toLowerCase()
    );
  }

  /**
   * Obtenir les items par niveau
   */
  getItemsByLevel(minLevel: number, maxLevel: number): DofusItem[] {
    return RETRO_ITEMS_DATABASE.filter(item => 
      item.level >= minLevel && item.level <= maxLevel
    );
  }

  /**
   * Obtenir les items les plus rentables
   */
  getMostProfitableItems(budget: number, limit: number = 10): Array<{
    item: DofusItem;
    marketInfo: any;
    estimatedProfit: number;
  }> {
    const profitableItems = [];
    
    for (const item of RETRO_ITEMS_DATABASE) {
      const marketInfo = this.getMarketInfo(item.id);
      const itemPrice = marketInfo.basePrice;
      
      if (itemPrice <= budget) {
        const estimatedProfit = marketInfo.maxPrice - itemPrice;
        const profitMargin = (estimatedProfit / itemPrice) * 100;
        
        // Filtrer les items avec au moins 20% de marge
        if (profitMargin >= 20) {
          profitableItems.push({
            item,
            marketInfo,
            estimatedProfit
          });
        }
      }
    }
    
    // Trier par profit estimé décroissant
    return profitableItems
      .sort((a, b) => b.estimatedProfit - a.estimatedProfit)
      .slice(0, limit);
  }

  /**
   * Obtenir les items avec une statistique spécifique
   */
  getItemsWithStat(statName: string): DofusItem[] {
    return RETRO_ITEMS_DATABASE.filter(item => 
      item.baseStats[statName] !== undefined || 
      item.maxStats[statName] !== undefined
    );
  }

  /**
   * Recherche avancée avec filtres multiples
   */
  advancedSearch(filters: {
    query?: string;
    type?: string;
    minLevel?: number;
    maxLevel?: number;
    maxPrice?: number;
    requiredStats?: string[];
    difficulty?: 'facile' | 'moyen' | 'difficile';
  }): DofusItem[] {
    let results = [...RETRO_ITEMS_DATABASE];

    // Filtre par query
    if (filters.query) {
      const query = filters.query.toLowerCase();
      results = results.filter(item => 
        item.name.toLowerCase().includes(query) ||
        item.type.toLowerCase().includes(query)
      );
    }

    // Filtre par type
    if (filters.type) {
      results = results.filter(item => 
        item.type.toLowerCase() === filters.type!.toLowerCase()
      );
    }

    // Filtre par niveau
    if (filters.minLevel !== undefined) {
      results = results.filter(item => item.level >= filters.minLevel!);
    }
    if (filters.maxLevel !== undefined) {
      results = results.filter(item => item.level <= filters.maxLevel!);
    }

    // Filtre par prix
    if (filters.maxPrice !== undefined) {
      results = results.filter(item => {
        const marketInfo = this.getMarketInfo(item.id);
        return marketInfo.basePrice <= filters.maxPrice!;
      });
    }

    // Filtre par stats requises
    if (filters.requiredStats && filters.requiredStats.length > 0) {
      results = results.filter(item => 
        filters.requiredStats!.some(stat => 
          item.baseStats[stat] !== undefined || item.maxStats[stat] !== undefined
        )
      );
    }

    // Filtre par difficulté
    if (filters.difficulty) {
      results = results.filter(item => {
        const marketInfo = this.getMarketInfo(item.id);
        return marketInfo.difficulty === filters.difficulty;
      });
    }

    return results;
  }

  /**
   * Obtenir des statistiques sur la base de données
   */
  getDatabaseStats() {
    const totalItems = RETRO_ITEMS_DATABASE.length;
    const itemsByType = RETRO_ITEMS_DATABASE.reduce((acc, item) => {
      acc[item.type] = (acc[item.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const avgLevel = Math.round(
      RETRO_ITEMS_DATABASE.reduce((sum, item) => sum + item.level, 0) / totalItems
    );

    return {
      totalItems,
      itemsByType,
      avgLevel,
      priceRange: {
        min: Math.min(...Object.values(RETRO_MARKET_PRICES).map(p => p.basePrice)),
        max: Math.max(...Object.values(RETRO_MARKET_PRICES).map(p => p.maxPrice))
      }
    };
  }
}