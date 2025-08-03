import axios from 'axios';
import { DofusItem, DofapiItem } from '../types';

export class DofapiService {
  private readonly baseUrl: string;
  private readonly axiosInstance;

  constructor() {
    this.baseUrl = process.env.DOFAPI_BASE_URL || 'https://api.dofusdb.fr';
    this.axiosInstance = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Forgemagerie-App/1.0'
      }
    });
  }

  async searchItem(query: string): Promise<DofapiItem[]> {
    try {
      const response = await this.axiosInstance.get('/items', {
        params: {
          'filter[name_like]': query,
          'page[size]': 20
        }
      });

      return response.data.data || [];
    } catch (error) {
      console.error('Erreur lors de la recherche d\'objets:', error);
      throw new Error('Impossible de rechercher les objets');
    }
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

  async getItemPrices(itemId: number): Promise<number> {
    try {
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const basePrice = Math.floor(Math.random() * 100000) + 10000;
      return basePrice;
    } catch (error) {
      console.error(`Erreur lors de la récupération du prix pour l'objet ${itemId}:`, error);
      return 50000;
    }
  }
}