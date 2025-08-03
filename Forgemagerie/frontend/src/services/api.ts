import axios from 'axios';
import { ApiResponse, ForgemagieAnalysis, SearchResult, DofusItem, Rune } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analysisApi = {
  analyzeItem: async (data: {
    itemName: string;
    targetStats: Record<string, number>;
    statsASupprimer?: Record<string, number>;
  }): Promise<ForgemagieAnalysis> => {
    const response = await api.post<ApiResponse<ForgemagieAnalysis>>('/analysis/analyze', data);
    if (!response.data.success) {
      throw new Error(response.data.error || 'Erreur lors de l\'analyse');
    }
    return response.data.data;
  },

  searchItems: async (query: string): Promise<SearchResult[]> => {
    const response = await api.get<ApiResponse<SearchResult[]>>('/analysis/search', {
      params: { query }
    });
    if (!response.data.success) {
      throw new Error(response.data.error || 'Erreur lors de la recherche');
    }
    return response.data.data;
  },

  getItemDetails: async (id: number): Promise<DofusItem> => {
    const response = await api.get<ApiResponse<DofusItem>>(`/analysis/items/${id}`);
    if (!response.data.success) {
      throw new Error(response.data.error || 'Erreur lors de la récupération de l\'objet');
    }
    return response.data.data;
  },

  getRunes: async (params?: { type?: string; effect?: string }): Promise<Rune[]> => {
    const response = await api.get<ApiResponse<Rune[]>>('/analysis/runes', { params });
    if (!response.data.success) {
      throw new Error(response.data.error || 'Erreur lors de la récupération des runes');
    }
    return response.data.data;
  },

  calculatePuits: async (data: {
    itemId: number;
    targetStats: Record<string, number>;
    statsASupprimer?: Record<string, number>;
  }): Promise<{
    puitsUtilise: number;
    puitsDisponible: number;
    puitsRestant: number;
    feasible: boolean;
  }> => {
    const response = await api.post('/analysis/calculate-puits', data);
    if (!response.data.success) {
      throw new Error(response.data.error || 'Erreur lors du calcul du puits');
    }
    return response.data.data;
  }
};

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      throw new Error(error.response.data?.error || 'Erreur serveur');
    } else if (error.request) {
      throw new Error('Impossible de contacter le serveur');
    } else {
      throw new Error('Erreur de requête');
    }
  }
);

export default api;