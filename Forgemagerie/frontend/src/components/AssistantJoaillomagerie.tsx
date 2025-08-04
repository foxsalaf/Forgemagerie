'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { 
  SparklesIcon, 
  CurrencyDollarIcon, 
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { assistantApi } from '@/services/api';
import { AssistantRequest, AssistantResponse, AssistantRecommendation, MarketInsights } from '@/types';
import toast from 'react-hot-toast';

interface FormData {
  server: string;
  budget: number;
  preferredStats: string[];
  riskTolerance: 'conservateur' | 'modere' | 'agressif';
  minProfitMargin: number;
  maxItemLevel: number;
  excludedTypes: string[];
}

const AVAILABLE_STATS = [
  { key: 'pa', label: 'PA', color: 'text-indigo-600' },
  { key: 'pm', label: 'PM', color: 'text-cyan-600' },
  { key: 'vitalite', label: 'Vitalité', color: 'text-green-600' },
  { key: 'force', label: 'Force', color: 'text-red-600' },
  { key: 'intelligence', label: 'Intelligence', color: 'text-blue-600' },
  { key: 'chance', label: 'Chance', color: 'text-yellow-600' },
  { key: 'agilite', label: 'Agilité', color: 'text-green-500' },
  { key: 'sagesse', label: 'Sagesse', color: 'text-purple-600' },
  { key: 'puissance', label: 'Puissance', color: 'text-orange-600' },
  { key: 'dommages', label: 'Dommages', color: 'text-red-500' },
  { key: 'portee', label: 'Portée', color: 'text-teal-600' },
  { key: 'coup_critique', label: 'Coups Critiques', color: 'text-yellow-500' },
  { key: 'soins', label: 'Soins', color: 'text-pink-600' },
];

const ITEM_TYPES = [
  'Amulette', 'Anneau', 'Bottes', 'Ceinture', 'Cape', 'Coiffe',
  'Épée', 'Dague', 'Arc', 'Bâton', 'Marteau', 'Pelle', 'Hache', 'Bouclier'
];

const SERVERS = [
  'retro', 'global', 'Agride', 'Allister', 'Brumen', 'Grandapan', 'Hellmina', 
  'Ily', 'Jahash', 'Merkator', 'Nidas', 'Oto-Mustam', 'Padgref', 
  'Rubilax', 'Ryuku', 'Temporis', 'Tylezia'
];

export default function AssistantJoaillomagerie() {
  const [recommendations, setRecommendations] = useState<AssistantResponse | null>(null);
  const [marketInsights, setMarketInsights] = useState<MarketInsights | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [budgetValidation, setBudgetValidation] = useState<any>(null);
  const [selectedStats, setSelectedStats] = useState<string[]>([]);
  const [excludedTypes, setExcludedTypes] = useState<string[]>([]);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      server: 'retro',
      budget: 100000,
      riskTolerance: 'modere',
      minProfitMargin: 15,
      maxItemLevel: 200,
      preferredStats: [],
      excludedTypes: []
    }
  });

  const watchedBudget = watch('budget');
  const watchedServer = watch('server');
  const watchedRiskTolerance = watch('riskTolerance');

  useEffect(() => {
    if (watchedBudget > 0) {
      validateBudget();
    }
  }, [watchedBudget, watchedRiskTolerance]);

  useEffect(() => {
    loadMarketInsights();
  }, [watchedServer]);

  const validateBudget = async () => {
    try {
      const validation = await assistantApi.validateBudget(watchedBudget, watchedRiskTolerance);
      setBudgetValidation(validation);
    } catch (error) {
      console.error('Erreur validation budget:', error);
    }
  };

  const loadMarketInsights = async () => {
    try {
      const insights = await assistantApi.getMarketInsights(watchedServer);
      setMarketInsights(insights);
    } catch (error) {
      console.error('Erreur insights marché:', error);
    }
  };

  const toggleStat = (stat: string) => {
    const newStats = selectedStats.includes(stat)
      ? selectedStats.filter(s => s !== stat)
      : [...selectedStats, stat];
    setSelectedStats(newStats);
    setValue('preferredStats', newStats);
  };

  const toggleExcludedType = (type: string) => {
    const newTypes = excludedTypes.includes(type)
      ? excludedTypes.filter(t => t !== type)
      : [...excludedTypes, type];
    setExcludedTypes(newTypes);
    setValue('excludedTypes', newTypes);
  };

  const onSubmit = async (data: FormData) => {
    if (selectedStats.length === 0) {
      toast.error('Veuillez sélectionner au moins une statistique préférée');
      return;
    }

    setIsLoading(true);
    try {
      const request: AssistantRequest = {
        ...data,
        preferredStats: selectedStats,
        excludedTypes: excludedTypes
      };

      console.log('Requête assistant:', request);
      const response = await assistantApi.getRecommendations(request);
      setRecommendations(response);
      
      if (response.recommendations.length === 0) {
        toast.error('Aucune recommandation trouvée avec ces critères');
      } else {
        toast.success(`${response.recommendations.length} recommandations générées!`);
      }
    } catch (error: any) {
      toast.error(error.message || 'Erreur lors de la génération des recommandations');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'facile': return 'text-green-600 bg-green-50';
      case 'moyen': return 'text-yellow-600 bg-yellow-50';
      case 'difficile': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatKamas = (amount: number) => {
    return new Intl.NumberFormat('fr-FR').format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="dofus-card p-6">
        <div className="flex items-center mb-4">
          <SparklesIcon className="h-8 w-8 text-purple-600 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Assistant Joaillomagerie IA</h1>
            <p className="text-gray-600">Recommandations personnalisées basées sur votre budget et vos préférences</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulaire */}
        <div className="lg:col-span-2">
          <div className="dofus-card p-6">
            <h2 className="text-xl font-semibold mb-6">Configuration</h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Serveur et Budget */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Serveur
                  </label>
                  <select
                    {...register('server', { required: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {SERVERS.map(server => (
                      <option key={server} value={server}>{server}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget (kamas)
                  </label>
                  <input
                    {...register('budget', { 
                      required: true, 
                      min: 10000,
                      valueAsNumber: true 
                    })}
                    type="number"
                    min="10000"
                    step="1000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="100000"
                  />
                  {errors.budget && <p className="text-red-500 text-sm mt-1">Budget minimum: 10,000 kamas</p>}
                </div>
              </div>

              {/* Validation du budget */}
              {budgetValidation && (
                <div className={`p-4 rounded-lg border ${
                  budgetValidation.valid 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-start">
                    {budgetValidation.valid ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 mr-2" />
                    ) : (
                      <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mt-0.5 mr-2" />
                    )}
                    <div className="text-sm">
                      <p className="font-medium mb-1">
                        Budget {budgetValidation.category} ({formatKamas(watchedBudget)} kamas)
                      </p>
                      <p>{budgetValidation.recommendation}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Statistiques préférées */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Statistiques préférées (sélectionnez vos priorités)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {AVAILABLE_STATS.map(stat => (
                    <button
                      key={stat.key}
                      type="button"
                      onClick={() => toggleStat(stat.key)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedStats.includes(stat.key)
                          ? 'bg-purple-100 text-purple-700 border-2 border-purple-300'
                          : 'bg-gray-50 text-gray-700 border-2 border-gray-200 hover:bg-gray-100'
                      }`}
                    >
                      {stat.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Paramètres avancés */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tolérance au risque
                  </label>
                  <select
                    {...register('riskTolerance')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="conservateur">Conservateur</option>
                    <option value="modere">Modéré</option>
                    <option value="agressif">Agressif</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Marge min (%)
                  </label>
                  <input
                    {...register('minProfitMargin', { valueAsNumber: true })}
                    type="number"
                    min="5"
                    max="100"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Niveau max
                  </label>
                  <input
                    {...register('maxItemLevel', { valueAsNumber: true })}
                    type="number"
                    min="1"
                    max="200"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Types exclus */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Types d'items à exclure (optionnel)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {ITEM_TYPES.map(type => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => toggleExcludedType(type)}
                      className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                        excludedTypes.includes(type)
                          ? 'bg-red-100 text-red-700 border border-red-300'
                          : 'bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || selectedStats.length === 0}
                className="dofus-button w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Génération des recommandations...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="h-5 w-5 mr-2" />
                    Obtenir mes recommandations
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Insights marché */}
        <div className="space-y-6">
          {marketInsights && (
            <div className="dofus-card p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <ChartBarIcon className="h-5 w-5 mr-2 text-blue-600" />
                Insights Marché
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Items populaires</h4>
                  {marketInsights.hotItems.slice(0, 3).map((item, index) => (
                    <div key={index} className="flex justify-between items-center py-1">
                      <span className="text-sm">{item.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        item.demand === 'high' ? 'bg-green-100 text-green-700' :
                        item.demand === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {item.demand}
                      </span>
                    </div>
                  ))}
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Stats rentables</h4>
                  {marketInsights.profitableStats.slice(0, 3).map((stat, index) => (
                    <div key={index} className="flex justify-between items-center py-1">
                      <span className="text-sm">{stat.stat}</span>
                      <span className="text-xs text-green-600">+{stat.avgProfit}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recommandations */}
      {recommendations && (
        <div className="dofus-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Recommandations</h2>
            <div className="text-sm text-gray-600">
              Budget utilisé: {formatKamas(recommendations.totalBudgetUsed)} / {formatKamas(watchedBudget)} kamas
            </div>
          </div>

          {/* Analyse du marché */}
          {recommendations.marketAnalysis.bestOpportunities.length > 0 && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">💡 Opportunités détectées</h3>
              <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                {recommendations.marketAnalysis.bestOpportunities.map((opportunity, index) => (
                  <li key={index}>{opportunity}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Avertissements */}
          {recommendations.marketAnalysis.warnings.length > 0 && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h3 className="font-semibold text-yellow-900 mb-2 flex items-center">
                <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                Avertissements
              </h3>
              <ul className="list-disc list-inside text-sm text-yellow-800 space-y-1">
                {recommendations.marketAnalysis.warnings.map((warning, index) => (
                  <li key={index}>{warning}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Liste des recommandations */}
          <div className="space-y-4">
            {recommendations.recommendations.map((rec, index) => (
              <RecommendationCard key={index} recommendation={rec} />
            ))}
          </div>

          {/* Résumé */}
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">📊 Résumé</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-green-700">Recommandations:</span>
                <div className="font-semibold">{recommendations.recommendations.length}</div>
              </div>
              <div>
                <span className="text-green-700">Investissement:</span>
                <div className="font-semibold">{formatKamas(recommendations.totalBudgetUsed)} k</div>
              </div>
              <div>
                <span className="text-green-700">Profit estimé:</span>
                <div className="font-semibold text-green-600">+{formatKamas(recommendations.estimatedTotalProfit)} k</div>
              </div>
              <div>
                <span className="text-green-700">ROI moyen:</span>
                <div className="font-semibold text-green-600">
                  +{Math.round((recommendations.estimatedTotalProfit / recommendations.totalBudgetUsed) * 100)}%
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function RecommendationCard({ recommendation }: { recommendation: AssistantRecommendation }) {
  const formatKamas = (amount: number) => new Intl.NumberFormat('fr-FR').format(amount);
  
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-lg text-gray-900">{recommendation.item.name}</h4>
          <p className="text-sm text-gray-600">{recommendation.item.type} • Niveau {recommendation.item.level}</p>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-green-600">
            +{formatKamas(recommendation.analysis.expectedProfit)} k
          </div>
          <div className="text-sm text-gray-600">
            {recommendation.profitMargin.toFixed(1)}% marge
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
        <div className="text-center">
          <div className="text-sm text-gray-600">Coût total</div>
          <div className="font-semibold">{formatKamas(recommendation.analysis.totalCost)} k</div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600">Difficulté</div>
          <div className={`px-2 py-1 rounded text-sm font-medium ${
            recommendation.difficulty === 'facile' ? 'bg-green-100 text-green-700' :
            recommendation.difficulty === 'moyen' ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          }`}>
            {recommendation.difficulty}
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600">Temps estimé</div>
          <div className="font-semibold flex items-center justify-center">
            <ClockIcon className="h-4 w-4 mr-1" />
            {recommendation.estimatedTime}min
          </div>
        </div>
        
        <div className="text-center">
          <div className="text-sm text-gray-600">Puits utilisé</div>
          <div className="font-semibold">
            {recommendation.analysis.puitsUtilise}/{recommendation.item.puits}
          </div>
        </div>
      </div>

      <div className="mb-3">
        <div className="text-sm text-gray-600 mb-1">Stats cibles:</div>
        <div className="flex flex-wrap gap-1">
          {Object.entries(recommendation.analysis.targetStats).map(([stat, value]) => (
            <span key={stat} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
              {stat}: {value}
            </span>
          ))}
        </div>
      </div>

      <div className="p-3 bg-gray-50 rounded text-sm text-gray-700">
        <strong>Pourquoi cette recommandation:</strong> {recommendation.reasoning}
      </div>
    </div>
  );
}