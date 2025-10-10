import React, { useState, useEffect } from 'react';
import { InterviewResult } from '@/lib/api';
import InsightAnalysis from './InsightAnalysis';
import ChatStyleInterview from './ChatStyleInterview';

interface PersonaInterviewSummary {
  personaName: string;
  mainFindings: string;
  mainImplications: string;
  initialInterview: InterviewResult[];
  additionalInterview?: InterviewResult[];
  personaDetails?: Record<string, string>;
}

interface ComprehensiveAnalysisViewProps {
  personaSummaries: PersonaInterviewSummary[];
  finalInsight: string;
  onAdditionalInterview?: () => void;
  loading?: boolean;
  forceActiveTab?: 'summary' | 'insights' | number;
}

const ComprehensiveAnalysisView: React.FC<ComprehensiveAnalysisViewProps> = ({
  personaSummaries,
  finalInsight,
  onAdditionalInterview,
  loading,
  forceActiveTab
}) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'insights' | number>('summary');

  // forceActiveTabが変更されたときにactiveTabを更新
  useEffect(() => {
    if (forceActiveTab !== undefined) {
      setActiveTab(forceActiveTab);
    }
  }, [forceActiveTab]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">分析結果</h2>
        <p className="text-gray-600">
          インタビュー結果とインサイト分析の総合ビュー
        </p>
      </div>

      {/* タブナビゲーション */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('summary')}
            className={`${
              activeTab === 'summary'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            📊 サマリ
          </button>
          
          {personaSummaries.map((summary, index) => (
            <button
              key={index}
              onClick={() => setActiveTab(index)}
              className={`${
                activeTab === index
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              👤 {summary.personaName}
            </button>
          ))}
          
          <button
            onClick={() => setActiveTab('insights')}
            className={`${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            🎯 最終インサイト
          </button>
        </nav>
      </div>

      {/* タブコンテンツ */}
      <div className="mt-6">
        {activeTab === 'summary' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">インタビューサマリ</h3>
            {personaSummaries.map((summary, index) => (
              <div key={index} className="bg-white border-2 border-gray-200 rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <h4 className="text-lg font-semibold text-gray-900">{summary.personaName}</h4>
                </div>
                
                <div className="space-y-3">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm font-medium text-blue-900 mb-2">💡 主な発見</p>
                    <p className="text-gray-700 whitespace-pre-wrap">{summary.mainFindings}</p>
                  </div>
                  
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm font-medium text-green-900 mb-2">📌 主な示唆</p>
                    <p className="text-gray-700 whitespace-pre-wrap">{summary.mainImplications}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {typeof activeTab === 'number' && personaSummaries[activeTab] && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {personaSummaries[activeTab].personaName} - インタビュー詳細
            </h3>
            
            {/* LINE風インタビュー表示 */}
            <div className="bg-white border-2 border-blue-200 rounded-lg p-8">
              <h4 className="text-lg font-semibold text-blue-900 mb-6">💬 インタビュー会話</h4>
              <div className="h-[600px]">
                <ChatStyleInterview
                  personaName={personaSummaries[activeTab].personaName}
                  allInterviews={[
                    ...personaSummaries[activeTab].initialInterview,
                    ...(personaSummaries[activeTab].additionalInterview || [])
                  ]}
                  personaDetails={personaSummaries[activeTab].personaDetails}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-6">
            <InsightAnalysis 
              analysis={finalInsight} 
              title="🎯 最終マーケティング戦略分析"
            />
          </div>
        )}
      </div>

      {/* 追加質問インタビューボタン */}
      {onAdditionalInterview && activeTab === 'insights' && (
        <div className="mt-8 flex justify-center">
          <button
            onClick={onAdditionalInterview}
            disabled={loading}
            className="bg-orange-600 text-white py-3 px-8 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? '処理中...' : '+ 追加質問インタビューを実施'}
          </button>
        </div>
      )}
    </div>
  );
};

export default ComprehensiveAnalysisView;


