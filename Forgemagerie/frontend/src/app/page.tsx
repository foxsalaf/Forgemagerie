'use client';

import { useState } from 'react';
import AnalyseObjetForm from '@/components/AnalyseObjetForm';
import ResultatFMTable from '@/components/ResultatFMTable';
import AssistantJoaillomagerie from '@/components/AssistantJoaillomagerie';
import { ForgemagieAnalysis } from '@/types';
import { InformationCircleIcon, SparklesIcon, ChartBarIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const [analysis, setAnalysis] = useState<ForgemagieAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState<'analyse' | 'assistant'>('analyse');

  const handleAnalysisComplete = (newAnalysis: ForgemagieAnalysis) => {
    setAnalysis(newAnalysis);
  };

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4 font-dofus">
          🔨 Forgemagerie Dofus
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Analysez la rentabilité de vos forgemagie en temps réel. 
          Optimisez vos profits avec les recommandations de runes intelligentes.
        </p>
      </div>

      {/* Navigation tabs */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('analyse')}
            className={`px-6 py-3 rounded-md font-medium transition-colors flex items-center ${
              activeTab === 'analyse'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <ChartBarIcon className="h-5 w-5 mr-2" />
            Analyse Manuelle
          </button>
          <button
            onClick={() => setActiveTab('assistant')}
            className={`px-6 py-3 rounded-md font-medium transition-colors flex items-center ${
              activeTab === 'assistant'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <SparklesIcon className="h-5 w-5 mr-2" />
            Assistant IA
          </button>
        </div>
      </div>

      {activeTab === 'analyse' && (
        <>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <InformationCircleIcon className="h-6 w-6 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
              <div className="text-blue-800">
                <h3 className="font-semibold mb-2">Comment utiliser l'analyse manuelle :</h3>
                <ol className="list-decimal list-inside space-y-1 text-sm">
                  <li>Recherchez et sélectionnez l'objet que vous souhaitez forgemager</li>
                  <li>Définissez les statistiques cibles que vous voulez atteindre</li>
                  <li>Optionnel: Indiquez les stats à supprimer pour libérer du puits</li>
                  <li>Lancez l'analyse pour obtenir les recommandations et la rentabilité</li>
                </ol>
                <p className="text-xs mt-2 text-blue-600">
                  💡 Les prix sont mis à jour automatiquement depuis les données du marché HDV
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'assistant' && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-8">
          <div className="flex items-start">
            <SparklesIcon className="h-6 w-6 text-purple-600 mr-3 mt-0.5 flex-shrink-0" />
            <div className="text-purple-800">
              <h3 className="font-semibold mb-2">Assistant Joaillomagerie IA :</h3>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>Renseignez votre budget en kamas et votre serveur</li>
                <li>Sélectionnez vos statistiques préférées (PA, PM, Vitalité...)</li>
                <li>Choisissez votre tolérance au risque</li>
                <li>Obtenez des recommandations personnalisées avec analyses complètes</li>
              </ul>
              <p className="text-xs mt-2 text-purple-600">
                🤖 L'IA analyse le marché en temps réel pour vous proposer les meilleures opportunités
              </p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'analyse' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <AnalyseObjetForm onAnalysisComplete={handleAnalysisComplete} />
          </div>
          
          <div>
            {analysis ? (
              <ResultatFMTable analysis={analysis} />
            ) : (
              <div className="dofus-card p-8 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Aucune analyse disponible
                </h3>
                <p className="text-gray-600">
                  Sélectionnez un objet et définissez vos statistiques cibles pour commencer l'analyse de rentabilité.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'assistant' && (
        <AssistantJoaillomagerie />
      )}

      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-amber-800 mb-4">
          📊 Statistiques et Fonctionnalités
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div>
            <h3 className="font-semibold text-amber-700 mb-2">Calculs Précis</h3>
            <ul className="text-amber-600 space-y-1">
              <li>• Calcul du puits selon les règles officielles</li>
              <li>• Optimisation des combinaisons de runes</li>
              <li>• Probabilités de réussite réalistes</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-amber-700 mb-2">Données Live</h3>
            <ul className="text-amber-600 space-y-1">
              <li>• Prix HDV mis à jour régulièrement</li>
              <li>• Base de données complète des objets</li>
              <li>• Informations via DofAPI</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-amber-700 mb-2">Analyse Avancée</h3>
            <ul className="text-amber-600 space-y-1">
              <li>• Scénarios SC/SN/EC détaillés</li>
              <li>• Calcul de rentabilité automatique</li>
              <li>• Recommandations intelligentes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}