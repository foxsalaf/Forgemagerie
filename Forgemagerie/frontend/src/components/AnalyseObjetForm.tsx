'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { MagnifyingGlassIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import { analysisApi } from '@/services/api';
import { SearchResult, ForgemagieAnalysis } from '@/types';
import toast from 'react-hot-toast';

interface FormData {
  itemName: string;
  targetStats: Record<string, number>;
  statsASupprimer: Record<string, number>;
}

interface Props {
  onAnalysisComplete: (analysis: ForgemagieAnalysis) => void;
}

const AVAILABLE_STATS = [
  { key: 'vitalite', label: 'Vitalité', color: 'text-green-600' },
  { key: 'force', label: 'Force', color: 'text-red-600' },
  { key: 'intelligence', label: 'Intelligence', color: 'text-blue-600' },
  { key: 'chance', label: 'Chance', color: 'text-yellow-600' },
  { key: 'agilite', label: 'Agilité', color: 'text-green-500' },
  { key: 'sagesse', label: 'Sagesse', color: 'text-purple-600' },
  { key: 'puissance', label: 'Puissance', color: 'text-orange-600' },
  { key: 'dommages', label: 'Dommages', color: 'text-red-500' },
  { key: 'pa', label: 'PA', color: 'text-indigo-600' },
  { key: 'pm', label: 'PM', color: 'text-cyan-600' },
  { key: 'portee', label: 'Portée', color: 'text-teal-600' },
  { key: 'coup_critique', label: 'Coups Critiques', color: 'text-yellow-500' },
  { key: 'soins', label: 'Soins', color: 'text-pink-600' },
];

export default function AnalyseObjetForm({ onAnalysisComplete }: Props) {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [selectedItem, setSelectedItem] = useState<SearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [targetStats, setTargetStats] = useState<Record<string, number>>({});
  const [statsASupprimer, setStatsASupprimer] = useState<Record<string, number>>({});

  const { register, handleSubmit, watch, setValue } = useForm<FormData>();

  const itemName = watch('itemName');

  const handleSearch = async (query: string) => {
    if (query.length < 3) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await analysisApi.searchItems(query);
      setSearchResults(results);
    } catch (error) {
      toast.error('Erreur lors de la recherche');
      console.error(error);
    } finally {
      setIsSearching(false);
    }
  };

  const selectItem = (item: SearchResult) => {
    setSelectedItem(item);
    setValue('itemName', item.name);
    setSearchResults([]);
  };

  const updateTargetStat = (stat: string, value: string) => {
    const numValue = parseInt(value) || 0;
    if (numValue === 0) {
      const newStats = { ...targetStats };
      delete newStats[stat];
      setTargetStats(newStats);
    } else {
      setTargetStats(prev => ({ ...prev, [stat]: numValue }));
    }
  };

  const updateStatASupprimer = (stat: string, value: string) => {
    const numValue = parseInt(value) || 0;
    if (numValue === 0) {
      const newStats = { ...statsASupprimer };
      delete newStats[stat];
      setStatsASupprimer(newStats);
    } else {
      setStatsASupprimer(prev => ({ ...prev, [stat]: numValue }));
    }
  };

  const onSubmit = async (data: FormData) => {
    if (!selectedItem) {
      toast.error('Veuillez sélectionner un objet');
      return;
    }

    if (Object.keys(targetStats).length === 0) {
      toast.error('Veuillez définir au moins une statistique cible');
      return;
    }

    setIsAnalyzing(true);
    try {
      const analysis = await analysisApi.analyzeItem({
        itemName: selectedItem.name,
        targetStats,
        statsASupprimer
      });
      
      onAnalysisComplete(analysis);
      toast.success('Analyse terminée avec succès!');
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de l\'analyse');
      console.error(error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="dofus-card p-6">
      <div className="flex items-center mb-6">
        <Cog6ToothIcon className="h-6 w-6 text-amber-600 mr-2" />
        <h2 className="text-xl font-bold text-gray-900">Analyse d'Objet</h2>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nom de l'objet
          </label>
          <div className="relative">
            <input
              {...register('itemName', { required: true })}
              type="text"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              placeholder="Tapez le nom de l'objet..."
              onChange={(e) => handleSearch(e.target.value)}
            />
            <MagnifyingGlassIcon className="absolute right-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>
          
          {searchResults.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {searchResults.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => selectItem(item)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b last:border-b-0 focus:bg-gray-50"
                >
                  <div className="font-medium text-gray-900">{item.name}</div>
                  <div className="text-sm text-gray-500">
                    {item.type} • Niveau {item.level}
                  </div>
                </button>
              ))}
            </div>
          )}
          
          {isSearching && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4 text-center text-gray-500">
              Recherche en cours...
            </div>
          )}
        </div>

        {selectedItem && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Objet sélectionné</h3>
            <div className="text-blue-800">
              <span className="font-medium">{selectedItem.name}</span>
              <span className="ml-2 text-sm">({selectedItem.type} • Niv. {selectedItem.level})</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Statistiques Cibles
            </h3>
            <div className="space-y-3">
              {AVAILABLE_STATS.map((stat) => (
                <div key={stat.key} className="flex items-center justify-between">
                  <label className={`text-sm font-medium ${stat.color}`}>
                    {stat.label}
                  </label>
                  <input
                    type="number"
                    min="0"
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-center focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    placeholder="0"
                    onChange={(e) => updateTargetStat(stat.key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Stats à Supprimer (pour libérer du puits)
            </h3>
            <div className="space-y-3">
              {AVAILABLE_STATS.map((stat) => (
                <div key={stat.key} className="flex items-center justify-between">
                  <label className={`text-sm font-medium ${stat.color}`}>
                    {stat.label}
                  </label>
                  <input
                    type="number"
                    min="0"
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-center focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    placeholder="0"
                    onChange={(e) => updateStatASupprimer(stat.key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <button
            type="submit"
            disabled={!selectedItem || Object.keys(targetStats).length === 0 || isAnalyzing}
            className="dofus-button w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyse en cours...
              </>
            ) : (
              'Analyser la Rentabilité'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}