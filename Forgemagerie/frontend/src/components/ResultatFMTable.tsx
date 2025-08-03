'use client';

import { ForgemagieAnalysis } from '@/types';
import { 
  ChartBarIcon, 
  CurrencyEuroIcon, 
  SparklesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface Props {
  analysis: ForgemagieAnalysis;
}

export default function ResultatFMTable({ analysis }: Props) {
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('fr-FR').format(Math.round(num));
  };

  const formatKamas = (num: number): string => {
    return `${formatNumber(num)} K`;
  };

  const getProfitabilityColor = (profitability: number): string => {
    if (profitability > 20) return 'text-green-600';
    if (profitability > 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProfitabilityIcon = (profitability: number) => {
    if (profitability > 20) return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    if (profitability > 5) return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
    return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
  };

  return (
    <div className="space-y-6">
      <div className="dofus-card p-6">
        <div className="flex items-center mb-6">
          <ChartBarIcon className="h-6 w-6 text-amber-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Résultats de l'Analyse</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {analysis.puitsUtilise}
            </div>
            <div className="text-sm text-blue-800">Puits Utilisé</div>
            <div className="text-xs text-blue-600 mt-1">
              / {analysis.puitsDisponible} disponible
            </div>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600 mb-1">
              {formatKamas(analysis.totalCost)}
            </div>
            <div className="text-sm text-purple-800">Coût Total Runes</div>
          </div>

          <div className={`bg-opacity-10 border rounded-lg p-4 text-center ${
            analysis.profitability > 20 ? 'bg-green-50 border-green-200' :
            analysis.profitability > 5 ? 'bg-yellow-50 border-yellow-200' :
            'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center justify-center mb-1">
              {getProfitabilityIcon(analysis.profitability)}
              <span className={`text-2xl font-bold ml-2 ${getProfitabilityColor(analysis.profitability)}`}>
                {analysis.profitability.toFixed(1)}%
              </span>
            </div>
            <div className={`text-sm ${getProfitabilityColor(analysis.profitability)}`}>
              Rentabilité
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-900 mb-3">
            Objet: {analysis.item.name}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Type:</span>
              <span className="ml-2 font-medium">{analysis.item.type}</span>
            </div>
            <div>
              <span className="text-gray-600">Niveau:</span>
              <span className="ml-2 font-medium">{analysis.item.level}</span>
            </div>
            <div>
              <span className="text-gray-600">Puits total:</span>
              <span className="ml-2 font-medium">{analysis.item.puits}</span>
            </div>
            <div>
              <span className="text-gray-600">Prix actuel:</span>
              <span className="ml-2 font-medium">{formatKamas(analysis.item.baseStats.prix || 0)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dofus-card p-6">
        <div className="flex items-center mb-4">
          <SparklesIcon className="h-6 w-6 text-amber-600 mr-2" />
          <h3 className="text-lg font-bold text-gray-900">Runes Recommandées</h3>
        </div>

        {analysis.recommendedRunes.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 font-medium text-gray-900">Rune</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-900">Effet</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-900">Poids</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-900">Type</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-900">Prix</th>
                </tr>
              </thead>
              <tbody>
                {analysis.recommendedRunes.map((rune, index) => (
                  <tr key={`${rune.id}-${index}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-2 font-medium text-gray-900">{rune.name}</td>
                    <td className="py-3 px-2 text-gray-600 capitalize">{rune.effect.replace('_', ' ')}</td>
                    <td className="py-3 px-2 text-gray-600">{rune.weight}</td>
                    <td className="py-3 px-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        rune.type === 'exo' ? 'bg-purple-100 text-purple-800' :
                        rune.type === 'ga' ? 'bg-blue-100 text-blue-800' :
                        rune.type === 'ra' ? 'bg-green-100 text-green-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {rune.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-right font-medium text-gray-900">
                      {formatKamas(rune.price)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center text-gray-500 py-8">
            Aucune rune recommandée pour cette configuration
          </div>
        )}
      </div>

      <div className="dofus-card p-6">
        <div className="flex items-center mb-4">
          <CurrencyEuroIcon className="h-6 w-6 text-amber-600 mr-2" />
          <h3 className="text-lg font-bold text-gray-900">Scénarios de Forgemagie</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {analysis.scenarios.map((scenario) => (
            <div 
              key={scenario.type}
              className={`border-2 rounded-lg p-4 ${
                scenario.type === 'SC' ? 'border-green-200 bg-green-50' :
                scenario.type === 'SN' ? 'border-yellow-200 bg-yellow-50' :
                'border-red-200 bg-red-50'
              }`}
            >
              <div className="text-center mb-3">
                <div className={`text-lg font-bold ${
                  scenario.type === 'SC' ? 'text-green-700' :
                  scenario.type === 'SN' ? 'text-yellow-700' :
                  'text-red-700'
                }`}>
                  {scenario.type === 'SC' ? 'Succès Critique' :
                   scenario.type === 'SN' ? 'Succès Neutre' :
                   'Échec Critique'}
                </div>
                <div className={`text-sm ${
                  scenario.type === 'SC' ? 'text-green-600' :
                  scenario.type === 'SN' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {(scenario.probability * 100).toFixed(0)}% de chance
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Valeur estimée:</span>
                  <span className="font-medium">{formatKamas(scenario.value)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Profit brut:</span>
                  <span className={`font-medium ${
                    (scenario.value - analysis.totalCost - (analysis.item.baseStats.prix || 0)) > 0 
                      ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatKamas(scenario.value - analysis.totalCost - (analysis.item.baseStats.prix || 0))}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-lg">
          <div className="text-center">
            <div className="text-lg font-bold text-amber-800 mb-1">
              Profit Espéré: {formatKamas(analysis.expectedProfit)}
            </div>
            <div className="text-sm text-amber-700">
              Basé sur les probabilités de réussite moyennes
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}