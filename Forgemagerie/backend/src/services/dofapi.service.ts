import axios from 'axios';
import { DofusItem, DofapiItem } from '../types';

export class DofapiService {
  private readonly baseUrl: string;
  private readonly axiosInstance;
  private apiAvailable: boolean = true;

  constructor() {
    // Utiliser la vraie DofAPI maintenant
    this.baseUrl = process.env.DOFAPI_BASE_URL || 'https://fr.dofus.dofapi.fr';
    this.axiosInstance = axios.create({
      baseURL: this.baseUrl,
      timeout: 8000, // Plus court pour éviter les timeouts
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Forgemagerie-App/1.0'
      }
    });

    // Interceptor pour gérer les erreurs
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND') {
          console.warn('🚨 DofAPI indisponible, basculement vers données locales');
          this.apiAvailable = false;
        }
        throw error;
      }
    );
  }

  async searchItem(query: string): Promise<DofapiItem[]> {
    if (!this.apiAvailable) {
      console.log('🔄 API indisponible, utilisation des données locales');
      return this.searchLocalItems(query);
    }

    try {
      // Essayer d'abord equipments puis weapons
      let response;
      try {
        response = await this.axiosInstance.get('/equipments');
      } catch (err) {
        console.log('🔄 Tentative avec /weapons...');
        response = await this.axiosInstance.get('/weapons');
      }

      if (!response.data) {
        console.warn('🚨 Pas de données reçues de DofAPI');
        return this.searchLocalItems(query);
      }

      // Filtrer localement par nom
      const items = Array.isArray(response.data) ? response.data : [];
      const filtered = items.filter((item: any) => 
        item.name && item.name.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 20);

      return this.convertToDofapiFormat(filtered);
    } catch (error) {
      console.error('Erreur lors de la recherche d\'objets:', error);
      this.apiAvailable = false;
      return this.searchLocalItems(query);
    }
  }

  private searchLocalItems(query: string): DofapiItem[] {
    const { MockDataService } = require('./mock-data.service');
    const localItems = MockDataService.getRetroItems();
    
    return localItems
      .filter((item: DofusItem) => 
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.type.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, 20)
      .map((item: DofusItem) => this.convertLocalToDofapi(item));
  }

  private convertToDofapiFormat(items: any[]): DofapiItem[] {
    return items.map((item: any) => ({
      id: item._id || item.id,
      name: { fr: item.name, en: item.name },
      type: { name: { fr: item.type || 'Equipment', en: item.type || 'Equipment' } },
      level: item.level || 1,
      statistics: this.extractStatistics(item)
    }));
  }

  private convertLocalToDofapi(item: DofusItem): DofapiItem {
    return {
      id: item.id,
      name: { fr: item.name, en: item.name },
      type: { name: { fr: item.type, en: item.type } },
      level: item.level,
      statistics: Object.entries(item.baseStats).map(([key, value]) => ({
        characteristic: { name: { fr: key, en: key } },
        from: value,
        to: item.maxStats[key] || value
      }))
    };
  }

  private extractStatistics(item: any): Array<{
    characteristic: { name: { fr: string; en: string } };
    from: number;
    to?: number;
  }> {
    if (!item.characteristics) return [];
    
    return item.characteristics.map((char: any) => ({
      characteristic: {
        name: { fr: char.name || 'stat', en: char.name || 'stat' }
      },
      from: char.min || char.value || 0,
      to: char.max || char.value || undefined
    }));
  }

  async getItemById(id: number): Promise<DofapiItem | null> {
    try {
      const response = await this.axiosInstance.get(`/items/${id}`);
      return response.data.data || null;
    } catch (error) {
      console.error(`Erreur lors de la récupération de l'objet ${id}:`, error);
      return null;
    }
  }

  convertToDofusItem(dofapiItem: DofapiItem): DofusItem {
    const baseStats: Record<string, number> = {};
    const maxStats: Record<string, number> = {};
    let totalWeight = 0;

    dofapiItem.statistics.forEach(stat => {
      const statName = this.mapStatName(stat.characteristic.name.fr);
      const minValue = stat.from;
      const maxValue = stat.to || stat.from;

      baseStats[statName] = minValue;
      maxStats[statName] = maxValue;

      const weight = this.getStatWeight(statName);
      totalWeight += Math.max(minValue, maxValue) * weight;
    });

    const puits = Math.round(totalWeight * 0.1);

    return {
      id: dofapiItem.id,
      name: dofapiItem.name.fr,
      type: dofapiItem.type.name.fr,
      level: dofapiItem.level,
      baseStats,
      maxStats,
      weight: totalWeight,
      puits
    };
  }

  private mapStatName(frenchName: string): string {
    const statMapping: Record<string, string> = {
      'Vitalité': 'vitalite',
      'Sagesse': 'sagesse',
      'Force': 'force',
      'Intelligence': 'intelligence',
      'Chance': 'chance',
      'Agilité': 'agilite',
      'Puissance': 'puissance',
      'Dommages': 'dommages',
      'Résistance neutre': 'resistance_neutre',
      'Résistance terre': 'resistance_terre',
      'Résistance feu': 'resistance_feu',
      'Résistance eau': 'resistance_eau',
      'Résistance air': 'resistance_air',
      'Point de mouvement': 'pm',
      'Point d\'action': 'pa',
      'Portée': 'portee',
      'Invocations': 'invocations',
      'Soins': 'soins',
      'Coups critiques': 'coup_critique',
      'Fuite': 'fuite',
      'Tacle': 'tacle',
      'Esquive PA': 'esquive_pa',
      'Esquive PM': 'esquive_pm',
      'Retrait PA': 'retrait_pa',
      'Retrait PM': 'retrait_pm'
    };

    return statMapping[frenchName] || frenchName.toLowerCase().replace(/\s+/g, '_');
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

  async getItemPrices(itemId: number, server: string = 'global'): Promise<number> {
    try {
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Prix spéciaux pour le serveur Retro (économie différente)
      if (server === 'retro') {
        return this.getRetroItemPrice(itemId);
      }
      
      const basePrice = Math.floor(Math.random() * 100000) + 10000;
      return basePrice;
    } catch (error) {
      console.error(`Erreur lors de la récupération du prix pour l'objet ${itemId}:`, error);
      return server === 'retro' ? 25000 : 50000;
    }
  }

  private getRetroItemPrice(itemId: number): number {
    // Prix typiques des items populaires sur le serveur Retro
    const retroPrices: Record<number, number> = {
      101: 45000,   // Gelano
      102: 85000,   // Anneau des Dragoeufs
      103: 120000,  // Bottes du Bouftou Royal
      104: 180000,  // Cape Bourbisk
      105: 150000,  // Amulette du Minotot
      106: 95000,   // Ceinture du Blop Royal
      107: 110000,  // Coiffe Lynx
      108: 75000,   // Dague du Crâne
      109: 135000,  // Bâton de Meriana
      110: 85000    // Bouclier du Minotot
    };

    const basePrice = retroPrices[itemId] || 50000;
    
    // Variation de marché ±15%
    const variation = (Math.random() - 0.5) * 0.3;
    return Math.round(basePrice * (1 + variation));
  }
}