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
  finalInsight?: string;
  customAnalysisResults?: any;
  onAdditionalInterview?: () => void;
  loading?: boolean;
  forceActiveTab?: 'summary' | 'insights' | number;
  onExportPptx?: () => void;
  exportingPptx?: boolean;
}

const ComprehensiveAnalysisView: React.FC<ComprehensiveAnalysisViewProps> = ({
  personaSummaries,
  finalInsight,
  customAnalysisResults,
  onAdditionalInterview,
  loading,
  forceActiveTab,
  onExportPptx,
  exportingPptx,
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
          
          <button
            onClick={() => setActiveTab('insights')}
            className={`${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            🎯 インサイト分析
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
            {customAnalysisResults ? (
              <div className="space-y-8">
                {customAnalysisResults.analysis_results?.market_structure && (
                  <div className="bg-white border-2 border-purple-200 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-purple-900 mb-4">📊 市場構造の理解</h3>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                        {customAnalysisResults.analysis_results.market_structure}
                      </pre>
                    </div>
                  </div>
                )}
                
                {customAnalysisResults.analysis_results?.customer_needs && (
                  <div className="bg-white border-2 border-blue-200 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-blue-900 mb-4">🎯 消費者ニーズの確認</h3>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                        {customAnalysisResults.analysis_results.customer_needs}
                      </pre>
                    </div>
                  </div>
                )}
                
                {customAnalysisResults.analysis_results?.product_improvement && (
                  <div className="bg-white border-2 border-green-200 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-green-900 mb-4">🔧 商品・サービスのブラッシュアップ</h3>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                        {customAnalysisResults.analysis_results.product_improvement}
                      </pre>
                    </div>
                  </div>
                )}
                
                {customAnalysisResults.analysis_results?.target_analysis && (
                  <div className="bg-white border-2 border-orange-200 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-orange-900 mb-4">🎯 ターゲット分析</h3>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                        {customAnalysisResults.analysis_results.target_analysis}
                      </pre>
                    </div>
                  </div>
                )}
                
                {customAnalysisResults.analysis_results?.improvement_analysis && (
                  <div className="bg-white border-2 border-teal-200 rounded-lg p-6">
                    <h3 className="text-xl font-semibold text-teal-900 mb-4">🔧 改善分析</h3>
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                        {customAnalysisResults.analysis_results.improvement_analysis}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ) : finalInsight ? (
              <InsightAnalysis 
                analysis={finalInsight} 
                title="🎯 最終マーケティング戦略分析"
              />
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>分析結果がありません</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* アクションボタン */}
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        {onAdditionalInterview && activeTab === 'insights' && (
          <button
            onClick={onAdditionalInterview}
            disabled={loading}
            className="bg-orange-600 text-white py-3 px-8 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {loading ? '処理中...' : '+ 追加質問インタビューを実施'}
          </button>
        )}

        {onExportPptx && (
          <button
            onClick={onExportPptx}
            disabled={exportingPptx}
            className="btn-primary flex items-center gap-2 py-3 px-8"
          >
            {exportingPptx ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                レポート生成中...
              </>
            ) : (
              <>
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                PowerPointでダウンロード
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default ComprehensiveAnalysisView;


