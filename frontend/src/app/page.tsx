'use client';

import React, { useState, useEffect } from 'react';
import { apiClient, Persona, InterviewResult, ProductService, Competitor, ProjectInfo } from '@/lib/api';
import PersonaCard from '@/components/PersonaCard';
import InterviewCard from '@/components/InterviewCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProductServiceForm from '@/components/ProductServiceForm';
import CompetitorForm from '@/components/CompetitorForm';

export default function Home() {
  const [step, setStep] = useState(0); // 0: プロジェクト情報入力から開始
  const [topic, setTopic] = useState('');
  const [productServices, setProductServices] = useState<ProductService[]>([]);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [productCount, setProductCount] = useState(1);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersonas, setSelectedPersonas] = useState<number[]>([]);
  const [questions, setQuestions] = useState<string[]>([]);
  const [interviewResults, setInterviewResults] = useState<Record<string, InterviewResult[]>>({});
  const [analysis, setAnalysis] = useState<string>('');
  const [hypothesisData, setHypothesisData] = useState<any>(null);
  const [hypothesisInterviewResults, setHypothesisInterviewResults] = useState<Record<string, InterviewResult[]>>({});
  const [finalAnalysis, setFinalAnalysis] = useState<string>('');
  const [loading, setLoading] = useState(true); // 初期状態でローディング
  const [error, setError] = useState<string>('');
  const [connectionStatus, setConnectionStatus] = useState<string>('connecting');
  const [progress, setProgress] = useState<number>(0);
  const [progressMessage, setProgressMessage] = useState<string>('');
  const [interviewHistory, setInterviewHistory] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    // API接続テストと履歴の読み込み
    const initializeApp = async () => {
      try {
        setConnectionStatus('connecting');
        
        // API接続テスト
        const connectionTest = await apiClient.testConnection();
        if (connectionTest.status === 'error') {
          setError(connectionTest.message);
          setConnectionStatus('error');
          setLoading(false);
          return;
        }
        
        setConnectionStatus('connected');
        
        // インタビュー履歴を読み込み
        try {
          const historyResponse = await apiClient.getInterviewHistory();
          setInterviewHistory(historyResponse.history);
        } catch (err) {
          console.warn('履歴の読み込みに失敗しました:', err);
        }
        
        // 初期の商品・サービス情報を設定
        setProductServices([{
          id: '1',
          name: '',
          target_audience: '',
          benefits: '',
          benefit_reason: '',
          basic_info: ''
        }]);
        
        setLoading(false);
      } catch (err: any) {
        console.error('アプリケーションの初期化に失敗しました:', err);
        setError('アプリケーションの初期化に失敗しました。ページを再読み込みしてください。');
        setConnectionStatus('error');
        setLoading(false);
      }
    };
    
    initializeApp();
  }, []);

  const handleGeneratePersonas = async () => {
    if (!topic.trim()) {
      setError('トピックを入力してください');
      return;
    }

    // 商品・サービス情報の検証
    for (const product of productServices) {
      if (!product.name.trim() || !product.target_audience.trim() || 
          !product.benefits.trim() || !product.benefit_reason.trim() || 
          !product.basic_info.trim()) {
        setError('すべての商品・サービス情報を入力してください');
        return;
      }
    }

    setLoading(true);
    setError('');
    setProgress(0);
    setProgressMessage('AIがペルソナを生成中...');
    
    try {
      setProgress(50);
      const projectInfo: ProjectInfo = {
        topic,
        products_services: productServices,
        competitors
      };
      
      const response = await apiClient.generatePersonas(projectInfo);
      setProgress(100);
      setProgressMessage('ペルソナ生成完了');
      setPersonas(response.personas);
      setStep(2);
    } catch (err: any) {
      setError('ペルソナの生成に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handlePersonaSelection = (personaId: number) => {
    setSelectedPersonas(prev => {
      if (prev.includes(personaId)) {
        return prev.filter(id => id !== personaId);
      } else if (prev.length < 3) {
        return [...prev, personaId];
      }
      return prev;
    });
  };

  const handleStartInterview = async () => {
    if (selectedPersonas.length !== 3) {
      setError('3つのペルソナを選択してください');
      return;
    }

    setLoading(true);
    setError('');
    setProgress(0);
    setProgressMessage('インタビュー準備中...');

    try {
      setProgress(25);
      await apiClient.selectPersonas(selectedPersonas);
      
      setProgress(50);
      setProgressMessage('トピック特化の質問を生成中...');
      
      // トピック特化の質問を生成
      const questionsResponse = await apiClient.getDefaultQuestions(topic);
      setQuestions(questionsResponse.questions);
      
      setProgress(100);
      setProgressMessage('準備完了');
      setStep(3);
    } catch (err: any) {
      setError('ペルソナの選択に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handleConductInterview = async () => {
    setLoading(true);
    setError('');
    setProgress(0);

    try {
      const results: Record<string, InterviewResult[]> = {};
      const totalPersonas = selectedPersonas.length;
      const totalQuestions = questions.length;
      
      for (let i = 0; i < selectedPersonas.length; i++) {
        // ペルソナごとの基本進行率を計算
        const baseProgress = Math.round((i / totalPersonas) * 100);
        
        setProgress(baseProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} のインタビューを開始中...`);
        
        // 質問ごとの詳細進行を表示するため、一時的に進行率を細かく更新
        let detailedProgress = baseProgress;
        const progressPerQuestion = Math.round((1 / totalPersonas) * 100 / totalQuestions);
        
        // インタビュー実行（実際の実装では質問ごとの進行は表示されませんが、
        // ここでは推定進行度を段階的に更新）
        const questionCount = questions.length;
        const estimatedTimePerQuestion = 1000; // 1秒あたり1質問と仮定
        
        // 段階的に進行状況を更新
        const updateProgressInterval = setInterval(() => {
          if (detailedProgress < baseProgress + Math.round((1 / totalPersonas) * 90)) {
            detailedProgress += 2;
            setProgress(detailedProgress);
            const currentQuestionEstimate = Math.min(
              Math.floor(((detailedProgress - baseProgress) / (100 / totalPersonas)) * questionCount) + 1,
              questionCount
            );
            setProgressMessage(
              `ペルソナ ${i + 1}/${totalPersonas}: 質問 ${currentQuestionEstimate}/${questionCount} を処理中...`
            );
          }
        }, estimatedTimePerQuestion);
        
        try {
          const response = await apiClient.conductInterview(i, questions);
          results[response.persona_name] = response.interview_results;
          
          // インタビュー完了時の進行率
          clearInterval(updateProgressInterval);
          const completedProgress = Math.round(((i + 1) / totalPersonas) * 100);
          setProgress(completedProgress);
          setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} のインタビュー完了`);
          
        } catch (personaError) {
          clearInterval(updateProgressInterval);
          throw personaError;
        }
      }
      
      setProgress(100);
      setProgressMessage('すべてのインタビューが完了しました');
      setInterviewResults(results);
      setStep(4);
    } catch (err: any) {
      setError('インタビューの実行に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handleGenerateAnalysis = async () => {
    setLoading(true);
    setError('');
    setProgress(0);
    setProgressMessage('初回インサイト分析を生成中...');

    try {
      setProgress(50);
      const response = await apiClient.generateAnalysis();
      setProgress(100);
      setProgressMessage('初回分析完了');
      setAnalysis(response.analysis);
      setStep(5);
    } catch (err: any) {
      setError('分析の生成に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handleGenerateHypothesis = async () => {
    setLoading(true);
    setError('');
    setProgress(0);
    setProgressMessage('仮説と追加質問を生成中...');

    try {
      setProgress(50);
      const response = await apiClient.generateHypothesis();
      setProgress(100);
      setProgressMessage('仮説生成完了');
      setHypothesisData(response);
      setStep(6);
    } catch (err: any) {
      setError('仮説の生成に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handleConductHypothesisInterview = async () => {
    setLoading(true);
    setError('');
    setProgress(0);

    try {
      const results: Record<string, InterviewResult[]> = {};
      const totalPersonas = selectedPersonas.length;
      const additionalQuestions = hypothesisData?.additional_questions || [];
      
      for (let i = 0; i < selectedPersonas.length; i++) {
        const baseProgress = Math.round((i / totalPersonas) * 100);
        setProgress(baseProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の仮説検証インタビューを実行中...`);
        
        const response = await apiClient.conductHypothesisInterview(i, additionalQuestions);
        results[response.persona_name] = response.interview_results;
        
        const completedProgress = Math.round(((i + 1) / totalPersonas) * 100);
        setProgress(completedProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の仮説検証完了`);
      }
      
      setProgress(100);
      setProgressMessage('仮説検証インタビュー完了');
      setHypothesisInterviewResults(results);
      setStep(7);
    } catch (err: any) {
      setError('仮説検証インタビューの実行に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handleGenerateFinalAnalysis = async () => {
    setLoading(true);
    setError('');
    setProgress(0);
    setProgressMessage('最終マーケティング戦略分析を生成中...');

    try {
      setProgress(50);
      const response = await apiClient.generateFinalAnalysis();
      setProgress(100);
      setProgressMessage('最終分析完了');
      setFinalAnalysis(response.final_analysis);
      setStep(8);
    } catch (err: any) {
      setError('最終分析の生成に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const addProduct = () => {
    const newProduct: ProductService = {
      id: (productServices.length + 1).toString(),
      name: '',
      target_audience: '',
      benefits: '',
      benefit_reason: '',
      basic_info: ''
    };
    setProductServices([...productServices, newProduct]);
  };

  const removeProduct = (id: string) => {
    setProductServices(productServices.filter(p => p.id !== id));
  };

  const updateProduct = (id: string, field: keyof ProductService, value: string) => {
    setProductServices(productServices.map(p => 
      p.id === id ? { ...p, [field]: value } : p
    ));
  };

  const addCompetitor = () => {
    const newCompetitor: Competitor = {
      name: '',
      description: '',
      price: '',
      features: ''
    };
    setCompetitors([...competitors, newCompetitor]);
  };

  const removeCompetitor = (index: number) => {
    setCompetitors(competitors.filter((_, i) => i !== index));
  };

  const updateCompetitor = (index: number, field: keyof Competitor, value: string) => {
    setCompetitors(competitors.map((c, i) => 
      i === index ? { ...c, [field]: value } : c
    ));
  };

  const handleExcelUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError('');
    
    try {
      const response = await apiClient.uploadExcelQuestions(file);
      setQuestions(response.questions);
      setError(''); // 成功時にエラーをクリア
      alert(`${response.count}個の質問を読み取りました`);
    } catch (err: any) {
      setError('Excelファイルの読み取りに失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                マーケティングインタビューシステム
              </h1>
              <p className="text-lg text-gray-600 mb-8">
                AIを活用してペルソナを生成し、深掘りインタビューでインサイトを発見します
              </p>
            </div>

            {/* 履歴表示ボタン */}
            {interviewHistory.length > 0 && (
              <div className="text-center mb-6">
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="bg-gray-600 text-white py-2 px-6 rounded-lg hover:bg-gray-700 font-medium"
                >
                  {showHistory ? '履歴を閉じる' : '過去の結果を見る'}
                </button>
              </div>
            )}

            {/* 履歴表示 */}
            {showHistory && (
              <div className="bg-gray-50 rounded-lg p-6 mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">過去のインタビュー履歴</h3>
                <div className="space-y-3">
                  {interviewHistory.map((history) => (
                    <div key={history.id} className="bg-white p-4 rounded border border-gray-200">
                      <div className="flex justify-between items-center">
                        <div>
                          <h4 className="font-medium text-gray-900">{history.topic}</h4>
                          <p className="text-sm text-gray-600">
                            {new Date(history.timestamp).toLocaleDateString('ja-JP')} - 
                            商品数: {history.products_count} - 
                            ペルソナ: {history.personas_used.join(', ')}
                          </p>
                        </div>
                        <button
                          onClick={async () => {
                            try {
                              const detail = await apiClient.getInterviewHistoryDetail(history.id);
                              alert('履歴詳細: ' + JSON.stringify(detail, null, 2));
                            } catch (err) {
                              setError('履歴の読み込みに失敗しました');
                            }
                          }}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          詳細を見る
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* トピック入力 */}
            <div className="space-y-4">
              <label className="block">
                <span className="text-lg font-medium text-gray-700">
                  インタビューしたい話題を入力してください
                </span>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="例: カラオケの新しい利用方法"
                  className="mt-2 block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </label>
            </div>

            {/* 商品・サービス情報入力 */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900">商品・サービス情報</h3>
                <button
                  onClick={addProduct}
                  className="bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 font-medium"
                >
                  + 商品・サービスを追加
                </button>
              </div>
              
              {productServices.map((product, index) => (
                <ProductServiceForm
                  key={product.id}
                  product={product}
                  index={index}
                  onUpdate={updateProduct}
                  onRemove={removeProduct}
                  canRemove={productServices.length > 1}
                />
              ))}
            </div>

            {/* 競合商品情報入力 */}
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900">競合商品・サービス情報</h3>
                <button
                  onClick={addCompetitor}
                  className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 font-medium"
                >
                  + 競合を追加
                </button>
              </div>
              
              {competitors.map((competitor, index) => (
                <CompetitorForm
                  key={index}
                  competitor={competitor}
                  index={index}
                  onUpdate={updateCompetitor}
                  onRemove={removeCompetitor}
                />
              ))}
              
              {competitors.length === 0 && (
                <div className="text-center py-6 text-gray-500">
                  <p>競合情報は任意です。必要に応じて追加してください。</p>
                </div>
              )}
            </div>

            <div className="flex justify-center">
              <button
                onClick={() => setStep(1)}
                disabled={loading || !topic.trim() || productServices.some(p => 
                  !p.name.trim() || !p.target_audience.trim() || !p.benefits.trim() || 
                  !p.benefit_reason.trim() || !p.basic_info.trim()
                )}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                次へ：ペルソナ生成
              </button>
            </div>
          </div>
        );

      case 1:
        return (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">ペルソナ生成</h2>
              <p className="text-lg text-gray-600 mb-8">
                入力された情報を基にAIがペルソナを生成します
              </p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-2">プロジェクト概要</h3>
              <p><strong>トピック:</strong> {topic}</p>
              <p><strong>商品・サービス数:</strong> {productServices.length}</p>
              <p><strong>競合数:</strong> {competitors.length}</p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setStep(0)}
                className="bg-gray-600 text-white py-3 px-6 rounded-lg hover:bg-gray-700 font-medium"
              >
                戻る
              </button>
              <button
                onClick={handleGeneratePersonas}
                disabled={loading}
                className="bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'ペルソナを生成'}
              </button>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">ペルソナを選択</h2>
              <p className="text-gray-600">
                インタビューしたい3名のペルソナを選択してください ({selectedPersonas.length}/3)
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {personas.map((persona) => (
                <PersonaCard
                  key={persona.id}
                  persona={persona}
                  isSelected={selectedPersonas.includes(persona.id)}
                  onSelect={handlePersonaSelection}
                />
              ))}
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setStep(1)}
                className="bg-gray-600 text-white py-3 px-6 rounded-lg hover:bg-gray-700 font-medium"
              >
                戻る
              </button>
              <button
                onClick={handleStartInterview}
                disabled={loading || selectedPersonas.length !== 3}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'インタビューを開始'}
              </button>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">インタビュー質問</h2>
              <p className="text-gray-600">
                以下の質問でインタビューを実行します。質問は編集可能です。
              </p>
            </div>
            
            {/* Excelアップロード */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-medium text-blue-900 mb-2">Excelファイルから質問を読み込み</h3>
              <p className="text-sm text-blue-700 mb-3">
                Excelファイルの最初の列から質問を自動で読み取ります
              </p>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleExcelUpload}
                disabled={loading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-600 file:text-white hover:file:bg-blue-700 disabled:opacity-50"
              />
            </div>
            
            {/* 質問操作ボタン */}
            <div className="flex justify-center space-x-4 mb-6">
              <button
                onClick={() => {
                  setQuestions([...questions, '']);
                }}
                className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 font-medium flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>質問を追加</span>
              </button>
              
              <button
                onClick={async () => {
                  try {
                    setLoading(true);
                    const response = await apiClient.getDefaultQuestions(topic);
                    setQuestions(response.questions);
                  } catch (err) {
                    setError('質問の再読み込みに失敗しました');
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading}
                className="bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>デフォルトに戻す</span>
              </button>
              
              <button
                onClick={() => {
                  setQuestions([]);
                }}
                className="bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 font-medium flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>全てクリア</span>
              </button>
            </div>
            
            <div className="space-y-4">
              {questions.map((question, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="block text-sm font-medium text-gray-700">
                      質問 {index + 1}
                    </label>
                    <button
                      onClick={() => {
                        const newQuestions = questions.filter((_, i) => i !== index);
                        setQuestions(newQuestions);
                      }}
                      className="text-red-600 hover:text-red-800 text-sm flex items-center space-x-1"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      <span>削除</span>
                    </button>
                  </div>
                  <textarea
                    value={question}
                    onChange={(e) => {
                      const newQuestions = [...questions];
                      newQuestions[index] = e.target.value;
                      setQuestions(newQuestions);
                    }}
                    placeholder="質問内容を入力してください..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={2}
                  />
                </div>
              ))}
              
              {questions.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>質問がありません。「質問を追加」または「デフォルトに戻す」ボタンを使用してください。</p>
                </div>
              )}
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setStep(2)}
                className="bg-gray-600 text-white py-3 px-6 rounded-lg hover:bg-gray-700 font-medium"
              >
                戻る
              </button>
              <button
                onClick={handleConductInterview}
                disabled={loading || questions.length === 0 || questions.some(q => !q.trim())}
                className="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" text="インタビューを実行中..." /> : 'インタビューを実行'}
              </button>
            </div>
            
            {questions.length > 0 && questions.some(q => !q.trim()) && (
              <div className="text-center text-sm text-red-600">
                空の質問があります。すべての質問に内容を入力してください。
              </div>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">インタビュー結果</h2>
              <p className="text-gray-600">
                各ペルソナとのインタビュー結果です
              </p>
            </div>
            
            {Object.entries(interviewResults).map(([personaName, results]) => (
              <div key={personaName} className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-900 border-b border-gray-200 pb-2">
                  {personaName}さんのインタビュー
                </h3>
                <div className="space-y-4">
                  {results.map((result, index) => (
                    <InterviewCard key={index} result={result} index={index} />
                  ))}
                </div>
              </div>
            ))}
            
            <div className="flex justify-center">
              <button
                onClick={handleGenerateAnalysis}
                disabled={loading}
                className="bg-purple-600 text-white py-3 px-8 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" text="分析を生成中..." /> : '初回インサイト分析を生成'}
              </button>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">初回インサイト分析結果</h2>
              <p className="text-gray-600">
                初回インタビューのインサイト分析
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="prose max-w-none">
                <div
                  className="text-gray-800 leading-relaxed whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: analysis.replace(/\n/g, '<br/>') }}
                />
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleGenerateHypothesis}
                disabled={loading}
                className="bg-orange-600 text-white py-3 px-8 rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" text="仮説を生成中..." /> : '仮説と追加質問を生成'}
              </button>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">マーケティング仮説と追加質問</h2>
              <p className="text-gray-600">
                初回分析から導出された仮説と検証のための追加質問
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="prose max-w-none">
                <div
                  className="text-gray-800 leading-relaxed whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: hypothesisData?.hypothesis_and_questions?.replace(/\n/g, '<br/>') || '' }}
                />
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-4">追加インタビュー質問</h3>
              <div className="space-y-2">
                {hypothesisData?.additional_questions?.map((question: string, index: number) => (
                  <div key={index} className="bg-white p-3 rounded border-l-4 border-blue-500">
                    <span className="text-sm font-medium text-blue-700">質問 {index + 1}:</span>
                    <p className="text-gray-800 mt-1">{question}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleConductHypothesisInterview}
                disabled={loading}
                className="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" text="仮説検証インタビューを実行中..." /> : '仮説検証インタビューを実行'}
              </button>
            </div>
          </div>
        );

      case 7:
        return (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">仮説検証インタビュー結果</h2>
              <p className="text-gray-600">
                各ペルソナとの仮説検証インタビュー結果
              </p>
            </div>
            
            {Object.entries(hypothesisInterviewResults).map(([personaName, results]) => (
              <div key={personaName} className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-900 border-b border-gray-200 pb-2">
                  {personaName}さんの仮説検証インタビュー
                </h3>
                <div className="space-y-4">
                  {results.map((result, index) => (
                    <InterviewCard key={index} result={result} index={index} />
                  ))}
                </div>
              </div>
            ))}
            
            <div className="flex justify-center">
              <button
                onClick={handleGenerateFinalAnalysis}
                disabled={loading}
                className="bg-purple-600 text-white py-3 px-8 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" text="最終分析を生成中..." /> : '最終マーケティング戦略分析を生成'}
              </button>
            </div>
          </div>
        );

      case 8:
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">最終マーケティング戦略分析</h2>
              <p className="text-gray-600">
                全インタビューを統合した最終的なマーケティング戦略提言
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="prose max-w-none">
                <div
                  className="text-gray-800 leading-relaxed whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: finalAnalysis.replace(/\n/g, '<br/>') }}
                />
              </div>
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={async () => {
                  try {
                    await apiClient.saveInterviewHistory();
                    alert('結果を履歴に保存しました');
                    
                    // 履歴を再読み込み
                    const historyResponse = await apiClient.getInterviewHistory();
                    setInterviewHistory(historyResponse.history);
                  } catch (err: any) {
                    setError('履歴の保存に失敗しました: ' + (err.response?.data?.detail || err.message));
                  }
                }}
                className="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 font-medium"
              >
                結果を保存
              </button>
              <button
                onClick={() => {
                  setStep(0);
                  setTopic('');
                  setProductServices([{
                    id: '1',
                    name: '',
                    target_audience: '',
                    benefits: '',
                    benefit_reason: '',
                    basic_info: ''
                  }]);
                  setCompetitors([]);
                  setPersonas([]);
                  setSelectedPersonas([]);
                  setQuestions([]);
                  setInterviewResults({});
                  setAnalysis('');
                  setHypothesisData(null);
                  setHypothesisInterviewResults({});
                  setFinalAnalysis('');
                }}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 font-medium"
              >
                新しいインタビューを開始
              </button>
              <button
                onClick={() => {
                  const element = document.createElement('a');
                  
                  // 商品・サービス情報をレポートに含める
                  let productsInfo = '';
                  productServices.forEach((product, index) => {
                    productsInfo += `
                    商品・サービス ${index + 1}: ${product.name}
                    ターゲット: ${product.target_audience}
                    ベネフィット: ${product.benefits}
                    根拠: ${product.benefit_reason}
                    基本情報: ${product.basic_info}
                    `;
                  });
                  
                  let competitorsInfo = '';
                  if (competitors.length > 0) {
                    competitorsInfo = '\n=== 競合情報 ===\n';
                    competitors.forEach((competitor, index) => {
                      competitorsInfo += `
                      競合 ${index + 1}: ${competitor.name}
                      説明: ${competitor.description}
                      価格: ${competitor.price || 'N/A'}
                      特徴: ${competitor.features || 'N/A'}
                      `;
                    });
                  }
                  
                  const file = new Blob([
                    `マーケティングインタビューシステム - 最終レポート\n\n`,
                    `トピック: ${topic}\n\n`,
                    `=== 商品・サービス情報 ===\n${productsInfo}\n`,
                    competitorsInfo,
                    `\n=== 初回インサイト分析 ===\n${analysis}\n\n`,
                    `=== 仮説と追加質問 ===\n${hypothesisData?.hypothesis_and_questions || ''}\n\n`,
                    `=== 最終マーケティング戦略分析 ===\n${finalAnalysis}\n\n`
                  ], { type: 'text/plain' });
                  element.href = URL.createObjectURL(file);
                  element.download = `マーケティング分析レポート_${topic}_${new Date().toISOString().split('T')[0]}.txt`;
                  document.body.appendChild(element);
                  element.click();
                  document.body.removeChild(element);
                }}
                className="bg-gray-600 text-white py-3 px-8 rounded-lg hover:bg-gray-700 font-medium"
              >
                レポートをダウンロード
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // 初期ロード画面
  if (loading && step === 0 && connectionStatus === 'connecting') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <h1 className="text-2xl font-bold text-gray-900 mt-4 mb-2">
            マーケティングインタビューシステム
          </h1>
          <p className="text-gray-600">
            {connectionStatus === 'connecting' ? 'サーバーに接続中...' : 'アプリケーションを初期化中...'}
          </p>
          {connectionStatus === 'error' && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                ページを再読み込み
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* プログレスバー */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-2">
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                    step >= stepNumber
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {stepNumber + 1}
                </div>
                {stepNumber < 8 && (
                  <div
                    className={`w-8 h-1 ${
                      step > stepNumber ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-2">
            <span className="text-xs text-gray-600">
              ステップ {step + 1} / 9
            </span>
          </div>
          <div className="flex justify-center mt-1">
            <span className="text-xs text-gray-500">
              {step === 0 && 'プロジェクト情報入力'}
              {step === 1 && 'ペルソナ生成'}
              {step === 2 && 'ペルソナ選択'}
              {step === 3 && 'インタビュー質問編集'}
              {step === 4 && '初回インタビュー実行'}
              {step === 5 && '初回インサイト分析'}
              {step === 6 && '仮説生成・追加質問'}
              {step === 7 && '仮説検証インタビュー'}
              {step === 8 && '最終マーケティング戦略分析'}
            </span>
          </div>
        </div>

        {/* 進行状況表示（ロード中のとき） */}
        {loading && progress > 0 && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="mb-2 flex justify-between items-center">
              <span className="text-sm font-medium text-blue-700">{progressMessage}</span>
              <span className="text-sm text-blue-600">{progress}%</span>
            </div>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* メインコンテンツ */}
        {renderStep()}
      </div>
    </div>
  );
}