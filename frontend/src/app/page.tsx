'use client';

import React, { useState, useEffect } from 'react';
import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { apiClient, Persona, InterviewResult, ProductService, Competitor, ProjectInfo } from '@/lib/api';
import PersonaCard from '@/components/PersonaCard';
import InterviewCard from '@/components/InterviewCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProductServiceForm from '@/components/ProductServiceForm';
import CompetitorForm from '@/components/CompetitorForm';
import ChatPersonaCard from '@/components/ChatPersonaCard';
import ChatInterview from '@/components/ChatInterview';
import InterviewResults from '@/components/InterviewResults';
import InsightAnalysis from '@/components/InsightAnalysis';
import ComprehensiveAnalysisView from '@/components/ComprehensiveAnalysisView';
import Sidebar from '@/components/Sidebar';

export default function Home() {
  // 認証状態の管理
  const { data: session, status } = useSession();
  const router = useRouter();
  
  // 未ログイン時はログイン画面にリダイレクト
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);
  // セッションID管理（マルチユーザー対応）
  const [sessionId, setSessionId] = useState<string>('');
  
  // 入力履歴管理
  const [inputHistory, setInputHistory] = useState<{
    products_services: any[];
    competitors: any[];
    topics: string[];
  }>({
    products_services: [],
    competitors: [],
    topics: []
  });
  const [showHistoryDropdown, setShowHistoryDropdown] = useState(false);
  
  const [step, setStep] = useState(0); // 0: プロジェクト情報入力から開始
  const [topic, setTopic] = useState('');
  const [productServices, setProductServices] = useState<ProductService[]>([]);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [productCount, setProductCount] = useState(1);
  const [personaCount, setPersonaCount] = useState(5);
  const [personaCharacteristics, setPersonaCharacteristics] = useState('');
  const [selectedAnalysisTypes, setSelectedAnalysisTypes] = useState<string[]>([]);
  const [interviewCount, setInterviewCount] = useState(3);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersonas, setSelectedPersonas] = useState<number[]>([]);
  const [questions, setQuestions] = useState<string[]>([]);
  const [interviewResults, setInterviewResults] = useState<Record<string, InterviewResult[]>>({});
  const [analysis, setAnalysis] = useState<string>('');
  const [hypothesisData, setHypothesisData] = useState<any>(null);
  const [hypothesisInterviewResults, setHypothesisInterviewResults] = useState<Record<string, InterviewResult[]>>({});
  const [finalAnalysis, setFinalAnalysis] = useState<string>('');
  const [finalStats, setFinalStats] = useState<any>(null);
  const [customAnalysisResults, setCustomAnalysisResults] = useState<any>(null);
  const [loading, setLoading] = useState(true); // 初期状態でローディング
  const [error, setError] = useState<string>('');
  const [connectionStatus, setConnectionStatus] = useState<string>('connecting');
  const [progress, setProgress] = useState<number>(0);
  const [progressMessage, setProgressMessage] = useState<string>('');
  const [interviewHistory, setInterviewHistory] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [personaSummaries, setPersonaSummaries] = useState<any[]>([]);
  const [showAdditionalQuestionDialog, setShowAdditionalQuestionDialog] = useState(false);
  const [additionalQuestions, setAdditionalQuestions] = useState<string[]>(['', '', '', '', '']);
  const [additionalInterviewResults, setAdditionalInterviewResults] = useState<Record<string, InterviewResult[]>>({});
  const [forceActiveTab, setForceActiveTab] = useState<'summary' | 'insights' | number | undefined>(undefined);
  const [exportingPptx, setExportingPptx] = useState(false);

  // ステップ定義
  const steps = [
    { id: 0, title: "プロジェクト設定", description: "商品情報とインタビュー対象者設定" },
    { id: 1, title: "インタビュー対象者選択", description: "インタビューする対象者を選択" },
    { id: 2, title: "質問内容作成", description: "インタビュー質問を作成" },
    { id: 3, title: "分析結果", description: "インタビューと分析結果" }
  ];

  const StepProgress = () => (
    <div className="mb-6 card p-4">
      <div className="flex items-center justify-center">
        <div className="flex items-center space-x-2">
          {steps.map((stepInfo, index) => (
            <React.Fragment key={stepInfo.id}>
              <div className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                    index < step
                      ? 'bg-green-500 text-white'
                      : index === step
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {index < step ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </div>
                <span className={`text-xs mt-1 text-center max-w-[80px] ${
                  index === step ? 'text-blue-600 font-medium' : 'text-gray-500'
                }`}>
                  {stepInfo.title}
                </span>
              </div>
              
              {index < steps.length - 1 && (
                <div className={`w-8 h-0.5 ${index < step ? 'bg-green-500' : 'bg-gray-200'}`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );

  useEffect(() => {
    // API接続テストと履歴の読み込み
    const initializeApp = async () => {
      try {
        setConnectionStatus('connecting');
        
        // セッションIDの初期化（マルチユーザー対応）
        let currentSessionId = localStorage.getItem('marketing_interview_session_id');
        if (!currentSessionId) {
          // 新しいセッションIDを生成
          currentSessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
          localStorage.setItem('marketing_interview_session_id', currentSessionId);
        }
        setSessionId(currentSessionId);
        console.log('セッションID:', currentSessionId);
        
        // API接続テスト
        const connectionTest = await apiClient.testConnection();
        if (connectionTest.status === 'error') {
          setError(connectionTest.message);
          setConnectionStatus('error');
          setLoading(false);
          return;
        }
        
        setConnectionStatus('connected');
        
        // 入力履歴を読み込み（localStorage）
        try {
          const savedHistory = localStorage.getItem('input_history');
          if (savedHistory) {
            const history = JSON.parse(savedHistory);
            setInputHistory(history);
            console.log('入力履歴を読み込みました:', history);
            
            // 最新の入力を自動記入（編集可能）
            if (history.topics && history.topics.length > 0) {
              setTopic(history.topics[history.topics.length - 1]);
            }
            if (history.products_services && history.products_services.length > 0) {
              const lastProduct = history.products_services[history.products_services.length - 1];
              setProductServices([lastProduct]);
            }
            if (history.competitors && history.competitors.length > 0) {
              setCompetitors(history.competitors.slice(-2)); // 最新2件
            }
          }
        } catch (err) {
          console.warn('入力履歴の読み込みに失敗しました:', err);
        }
        
        // インタビュー履歴を読み込み
        try {
          const historyResponse = await apiClient.getInterviewHistory();
          setInterviewHistory(historyResponse.history);
        } catch (err) {
          console.warn('履歴の読み込みに失敗しました:', err);
        }
        
        // 初期の商品・サービス情報を設定（入力履歴がない場合）
        if (productServices.length === 0) {
          setProductServices([{
            id: '1',
            name: '',
            target_audience: '',
            benefits: '',
            benefit_reason: '',
            basic_info: ''
          }]);
        }
        
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
    setProgressMessage('分析タイプを設定中...');
    
    try {
      // 分析タイプを設定
      if (selectedAnalysisTypes.length > 0) {
        setProgress(25);
        await apiClient.setAnalysisTypes(selectedAnalysisTypes);
        setProgressMessage('分析タイプ設定完了');
      }
      
      setProgress(50);
      setProgressMessage('AIがペルソナを生成中...');
      const projectInfo: ProjectInfo = {
        topic,
        products_services: productServices,
        competitors
      };
      
      const response = await apiClient.generatePersonas(
        projectInfo, 
        personaCount, 
        personaCharacteristics.trim() || undefined
      );
      setProgress(100);
      setProgressMessage('ペルソナ生成完了');
      setPersonas(response.personas);
      
      // 入力履歴をlocalStorageに保存
      const updatedHistory = {
        products_services: [...inputHistory.products_services, ...productServices].slice(-10), // 最新10件
        competitors: [...inputHistory.competitors, ...competitors].slice(-10),
        topics: [...inputHistory.topics, topic].filter((v, i, arr) => arr.indexOf(v) === i).slice(-10) // 重複削除
      };
      localStorage.setItem('input_history', JSON.stringify(updatedHistory));
      setInputHistory(updatedHistory);
      
      // 自動では画面遷移しない（編集可能にするため）
      // setStep(1); はユーザーが「次へ」ボタンを押した時のみ
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message;
      
      // APIオーバーロードエラーの場合は再試行を促す
      if (errorMessage.includes('過負荷') || 
          errorMessage.includes('overloaded') || 
          errorMessage.includes('503') ||
          errorMessage.includes('504') ||
          errorMessage.includes('timeout')) {
        setError('⚠️ APIが一時的に過負荷またはタイムアウト状態です。30秒ほど待ってから「ペルソナを生成」ボタンをもう一度クリックしてください。');
      } else {
        setError('ペルソナの生成に失敗しました: ' + errorMessage);
      }
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
      } else if (prev.length < interviewCount) {
        return [...prev, personaId];
      }
      return prev;
    });
  };

  const handleStartInterview = async () => {
    if (selectedPersonas.length !== interviewCount) {
      setError(`${interviewCount}人のインタビュー対象者を選択してください`);
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
      setStep(2);
    } catch (err: any) {
      setError('インタビュー対象者の選択に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage('');
    }
  };

  const handleAnalysisTypeSelection = async () => {
    if (selectedAnalysisTypes.length === 0) {
      setError('分析タイプを選択してください');
      return;
    }

    setLoading(true);
    setError('');
    setProgress(0);
    setProgressMessage('分析タイプを設定中...');

    try {
      setProgress(50);
      await apiClient.setAnalysisTypes(selectedAnalysisTypes);
      
      setProgress(100);
      setProgressMessage('設定完了');
      // 分析タイプ設定後は次のステップに進まず、そのままプロジェクト設定を続行
    } catch (err: any) {
      setError('分析タイプの設定に失敗しました: ' + (err.response?.data?.detail || err.message));
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
      // ステップ1: 初回インタビューを実行
      const results: Record<string, InterviewResult[]> = {};
      const totalPersonas = selectedPersonas.length;
      const totalQuestions = questions.length;
      
      setProgressMessage('初回インタビューを実行中...');
      for (let i = 0; i < selectedPersonas.length; i++) {
        const baseProgress = Math.round((i / (totalPersonas * 5)) * 100);
        setProgress(baseProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の初回インタビュー中...`);
        
        let detailedProgress = baseProgress;
        const progressPerQuestion = Math.round((1 / (totalPersonas * 5)) * 100 / totalQuestions);
        
        const questionCount = questions.length;
        const estimatedTimePerQuestion = 1000;
        
        const updateProgressInterval = setInterval(() => {
          if (detailedProgress < baseProgress + Math.round((1 / (totalPersonas * 5)) * 90)) {
            detailedProgress += 2;
            setProgress(detailedProgress);
            const currentQuestionEstimate = Math.min(
              Math.floor(((detailedProgress - baseProgress) / (100 / (totalPersonas * 5))) * questionCount) + 1,
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
          
          clearInterval(updateProgressInterval);
          const completedProgress = Math.round(((i + 1) / (totalPersonas * 5)) * 100);
          setProgress(completedProgress);
          setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の初回インタビュー完了`);
          
        } catch (personaError) {
          clearInterval(updateProgressInterval);
          throw personaError;
        }
      }
      
      setInterviewResults(results);
      setProgress(20);
      
      // ステップ2: インタビューサマリを生成
      setProgressMessage('インタビューサマリを生成中...');
      const summaryResponse = await apiClient.generateInterviewSummary();
      setProgress(30);
      
      // ステップ3: 初回分析を生成
      setProgressMessage('初回インサイト分析を生成中...');
      const analysisResponse = await apiClient.generateAnalysis();
      setAnalysis(analysisResponse.analysis);
      setProgress(40);
      
      // ステップ4: 仮説を生成
      setProgressMessage('マーケティング仮説と追加質問を生成中...');
      const hypothesisResponse = await apiClient.generateHypothesis();
      setHypothesisData(hypothesisResponse);
      setProgress(50);
      
      // ステップ5: 仮説検証インタビューを実行
      setProgressMessage('仮説検証インタビューを実行中...');
      const hypothesisResults: Record<string, InterviewResult[]> = {};
      
      const hypothesisText = hypothesisResponse.hypothesis_and_questions || '';
      const questionLines = hypothesisText.split('\n').filter(line => 
        line.trim().startsWith('Q') || 
        line.trim().match(/^\d+\./) ||
        line.trim().includes('？') || line.trim().includes('?')
      );
      
      const extractedQuestions = questionLines.map(line => 
        line.replace(/^[Q\d\.\s\-\*]+/, '').trim()
      ).filter(q => q.length > 5);
      
      for (let i = 0; i < selectedPersonas.length; i++) {
        const baseProgress = 50 + Math.round((i / totalPersonas) * 30);
        setProgress(baseProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の仮説検証インタビュー中...`);
        
        const response = await apiClient.conductHypothesisInterview(i, extractedQuestions);
        hypothesisResults[response.persona_name] = response.interview_results;
        
        const completedProgress = 50 + Math.round(((i + 1) / totalPersonas) * 30);
        setProgress(completedProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の仮説検証完了`);
      }
      
      setHypothesisInterviewResults(hypothesisResults);
      setProgress(80);
      
      // ステップ6: カスタム最終分析を生成
      setProgressMessage('選択された分析タイプに基づく分析を生成中...');
      const customFinalResponse = await apiClient.generateCustomFinalAnalysis();
      setCustomAnalysisResults(customFinalResponse);
      setFinalStats(customFinalResponse.stats);
      setProgress(90);
      
      // ステップ7: 統合サマリを作成
      setProgressMessage('統合分析を作成中...');
      const personaSummariesData = summaryResponse.summaries.map((summary: any) => {
        const personaName = summary.persona_name;
        const persona = selectedPersonas.find(p => p.name === personaName);
        return {
          personaName: personaName,
          mainFindings: summary.main_findings,
          mainImplications: summary.main_implications,
          initialInterview: results[personaName] || [],
          additionalInterview: hypothesisResults[personaName] || [],
          personaDetails: persona?.details || {}
        };
      });
      
      setPersonaSummaries(personaSummariesData);
      setProgress(100);
      setProgressMessage('分析完了');
      setStep(3);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message;
      
      // APIオーバーロードエラーの場合は再試行を促す
      if (errorMessage.includes('過負荷') || 
          errorMessage.includes('overloaded') || 
          errorMessage.includes('503') ||
          errorMessage.includes('504') ||
          errorMessage.includes('timeout')) {
        setError('⚠️ APIが一時的に過負荷またはタイムアウト状態です。30秒ほど待ってから「インタビューを実行」ボタンをもう一度クリックしてください。');
      } else {
        setError('インタビューまたは分析の実行に失敗しました: ' + errorMessage);
      }
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
      
      // 概要から質問を抽出（仮説検証質問の部分のみ）
      const hypothesisText = hypothesisData?.hypothesis_and_questions || '';
      const questionLines = hypothesisText.split('\n').filter(line => 
        line.trim().startsWith('Q') || 
        line.trim().match(/^\d+\./) ||
        line.trim().includes('？') || line.trim().includes('?')
      );
      
      // 質問を整理（番号や記号を除去）
      const extractedQuestions = questionLines.map(line => 
        line.replace(/^[Q\d\.\s\-\*]+/, '').trim()
      ).filter(q => q.length > 5); // 短すぎる質問を除外
      
      for (let i = 0; i < selectedPersonas.length; i++) {
        const baseProgress = Math.round((i / totalPersonas) * 100);
        setProgress(baseProgress);
        setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の仮説検証インタビューを実行中...`);
        
        const response = await apiClient.conductHypothesisInterview(i, extractedQuestions);
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
      setFinalStats(response.stats);
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

  const handleExportPptx = async () => {
    try {
      setExportingPptx(true);
      const blob = await apiClient.exportPptx(sessionId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tames_insight_report_${new Date().toISOString().slice(0, 10)}.pptx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('PPTX export error:', err);
      setError('PowerPointレポートの生成に失敗しました。');
    } finally {
      setExportingPptx(false);
    }
  };

  const renderStep = () => {
    // ステップ進行状況を表示（ローディング中やエラー時は非表示）
    const showProgress = !loading && !error && connectionStatus === 'connected';
  
  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">認証状態を確認中...</p>
        </div>
      </div>
    );
  }
  
  // 未ログイン時は何も表示しない（リダイレクト中）
  if (!session) {
    return null;
  }
    
    switch (step) {
      case 0:
  return (
          <div className="max-w-4xl mx-auto space-y-8">
            {showProgress && <StepProgress />}
            
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
                              
                              // 新しいウィンドウで詳細を表示
                              const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes');
                              if (newWindow) {
                                newWindow.document.write(`
                                  <html>
                                    <head>
                                      <title>tames interview - ${history.topic} - 分析結果</title>
                                      <meta charset="UTF-8">
                                      <style>
                                        body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }
                                        h1, h2, h3 { color: #333; }
                                        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
                                        .analysis { background-color: #f8f9fa; }
                                        .final-analysis { background-color: #e8f5e8; }
                                        pre { white-space: pre-wrap; word-wrap: break-word; }
                                      </style>
                                    </head>
                                    <body>
                                      <h1>📊 ${history.topic} - 分析結果</h1>
                                      <p><strong>実行日時:</strong> ${new Date(history.timestamp).toLocaleString('ja-JP')}</p>
                                      <p><strong>商品数:</strong> ${history.products_count}</p>
                                      <p><strong>インタビュー対象:</strong> ${history.personas_used.join(', ')}</p>
                                      
                                      ${detail.analysis ? `
                                        <div class="section analysis">
                                          <h2>🔍 初回インサイト分析</h2>
                                          <pre>${detail.analysis}</pre>
                                        </div>
                                      ` : ''}
                                      
                                      ${detail.final_analysis ? `
                                        <div class="section final-analysis">
                                          <h2>🎯 最終マーケティング戦略分析</h2>
                                          <pre>${detail.final_analysis}</pre>
                                        </div>
                                      ` : ''}
                                      
                                      ${detail.hypothesis_and_questions ? `
                                        <div class="section">
                                          <h2>💭 仮説と追加質問</h2>
                                          <pre>${detail.hypothesis_and_questions}</pre>
                                        </div>
                                      ` : ''}
                                    </body>
                                  </html>
                                `);
                                newWindow.document.close();
                              }
                            } catch (err) {
                              setError('履歴の読み込みに失敗しました');
                            }
                          }}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          📄 詳細を見る
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
                  placeholder="例: オンライン英会話サービス"
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

            {/* 分析タイプ選択 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-4">
              <h3 className="font-semibold text-blue-900 mb-4 text-xl">📊 分析目的の選択（複数選択可）</h3>
              <p className="text-sm text-blue-700 mb-4">
                インタビューの分析目的を選択してください。最終レポートで選択した内容に沿った分析が行われます。
              </p>
              
              <div className="space-y-3">
                <label className="flex items-start p-3 bg-white border-2 border-blue-200 rounded-lg hover:border-blue-400 cursor-pointer transition">
                  <input
                    type="checkbox"
                    checked={selectedAnalysisTypes.includes('market_structure')}
                  onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAnalysisTypes([...selectedAnalysisTypes, 'market_structure']);
                      } else {
                        setSelectedAnalysisTypes(selectedAnalysisTypes.filter(t => t !== 'market_structure'));
                    }
                  }}
                    className="mt-1 mr-3 h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
              <div>
                    <span className="font-medium text-gray-900">1. 市場構造の理解</span>
                    <p className="text-sm text-gray-600 mt-1">
                      市場全体の動向、顧客セグメント、競合状況を把握し、ビジネスチャンスを見出す分析
                </p>
              </div>
                </label>
                
                <label className="flex items-start p-3 bg-white border-2 border-blue-200 rounded-lg hover:border-blue-400 cursor-pointer transition">
                  <input
                    type="checkbox"
                    checked={selectedAnalysisTypes.includes('customer_needs')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAnalysisTypes([...selectedAnalysisTypes, 'customer_needs']);
                      } else {
                        setSelectedAnalysisTypes(selectedAnalysisTypes.filter(t => t !== 'customer_needs'));
                      }
                    }}
                    className="mt-1 mr-3 h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                        <div>
                    <span className="font-medium text-gray-900">2. ある特定の消費者ニーズの確認</span>
                    <p className="text-sm text-gray-600 mt-1">
                      特定の顧客層のニーズや課題を深掘りし、商品・サービスとのマッチングを検証する分析
                          </p>
                        </div>
                </label>
                
                <label className="flex items-start p-3 bg-white border-2 border-blue-200 rounded-lg hover:border-blue-400 cursor-pointer transition">
                  <input
                    type="checkbox"
                    checked={selectedAnalysisTypes.includes('product_improvement')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedAnalysisTypes([...selectedAnalysisTypes, 'product_improvement']);
                      } else {
                        setSelectedAnalysisTypes(selectedAnalysisTypes.filter(t => t !== 'product_improvement'));
                            }
                          }}
                    className="mt-1 mr-3 h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div>
                    <span className="font-medium text-gray-900">3. 商品・サービスのブラッシュアップ</span>
                    <p className="text-sm text-gray-600 mt-1">
                      現在の商品・サービスの改善点を発見し、より魅力的な価値提案を作り上げる分析
                    </p>
                  </div>
              </label>
            </div>

              {selectedAnalysisTypes.length === 0 && (
                <p className="text-sm text-red-600 mt-2">
                  ※ 少なくとも1つの分析目的を選択してください
                </p>
              )}
            </div>

            {/* インタビュー対象者選定設定 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
              <h3 className="font-semibold text-gray-900 mb-4 text-xl">インタビュー対象者選定設定</h3>
              
              <div>
                <label htmlFor="personaCount" className="block text-sm font-medium text-gray-700 mb-2">
                  選定するインタビュー対象者の人数
                </label>
                <select
                  id="personaCount"
                  value={personaCount}
                  onChange={(e) => {
                    const newPersonaCount = Number(e.target.value);
                    setPersonaCount(newPersonaCount);
                    // インタビュー人数が選定人数を超える場合は調整
                    if (interviewCount > newPersonaCount) {
                      setInterviewCount(newPersonaCount);
                    }
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {Array.from({ length: 13 }, (_, i) => i + 3).map(num => (
                    <option key={num} value={num}>{num}人</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="interviewCount" className="block text-sm font-medium text-gray-700 mb-2">
                  実際にインタビューする人数
                </label>
                <select
                  id="interviewCount"
                  value={interviewCount}
                  onChange={(e) => setInterviewCount(Number(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {Array.from({ length: personaCount }, (_, i) => i + 1).map(num => (
                    <option key={num} value={num}>{num}人</option>
                  ))}
                </select>
                <p className="text-sm text-gray-500 mt-1">
                  選定する人数以下で設定してください
                </p>
              </div>

              <div>
                <label htmlFor="personaCharacteristics" className="block text-sm font-medium text-gray-700 mb-2">
                  インタビュー対象者の特徴指定（任意）
                </label>
                <textarea
                  id="personaCharacteristics"
                  value={personaCharacteristics}
                  onChange={(e) => setPersonaCharacteristics(e.target.value)}
                  placeholder="例：20代〜40代の女性を中心に、健康意識が高い人、子育て中の母親を含める、など"
                  rows={3}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-sm text-gray-500 mt-1">
                  特定の年齢層、性別、職業、ライフスタイルなどの特徴があれば記載してください
                </p>
              </div>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={handleGeneratePersonas}
                disabled={loading || !topic.trim() || selectedAnalysisTypes.length === 0 || productServices.some(p => 
                  !p.name.trim() || !p.target_audience.trim() || !p.benefits.trim() || 
                  !p.benefit_reason.trim() || !p.basic_info.trim()
                )}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'インタビュー対象者を選定'}
              </button>
              
              {personas.length > 0 && !loading && (
                <button
                  onClick={() => setStep(1)}
                  className="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 font-medium flex items-center gap-2"
                >
                  <span>次へ</span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              )}
            </div>
            
            {personas.length > 0 && !loading && (
              <div className="text-center text-sm text-green-600">
                ✅ インタビュー対象者の選定が完了しました。内容を確認・編集してから「次へ」をクリックしてください。
              </div>
            )}
            
            {selectedAnalysisTypes.length === 0 && topic.trim() && (
              <div className="text-center text-sm text-red-600">
                分析目的を少なくとも1つ選択してください
              </div>
            )}
          </div>
        );

      case 1:
        return (
          <div className="space-y-6">
            {showProgress && <StepProgress />}
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">💬 インタビュー対象者を選択</h2>
              <p className="text-gray-600 mb-2">
                インタビューしたい{interviewCount}名の対象者を選択してください ({selectedPersonas.length}/{interviewCount})
              </p>
              <p className="text-sm text-gray-500">
                カードをクリックして選択してください
              </p>
            </div>
            
            {/* ペルソナグリッド表示 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
              {personas.map((persona) => (
                <ChatPersonaCard
                  key={persona.id}
                  persona={persona}
                  isSelected={selectedPersonas.includes(persona.id)}
                  onSelect={() => handlePersonaSelection(persona.id)}
                />
              ))}
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setStep(0)}
                className="bg-gray-600 text-white py-3 px-6 rounded-lg hover:bg-gray-700 font-medium"
              >
                戻る
              </button>
              <button
                onClick={handleStartInterview}
                disabled={loading || selectedPersonas.length !== interviewCount}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'インタビューを開始'}
              </button>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            {showProgress && <StepProgress />}
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">質問内容</h2>
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
                onClick={() => setStep(1)}
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

      case 3:
        return (
          <div className="max-w-7xl mx-auto space-y-8">
            {showProgress && <StepProgress />}
            
            {personaSummaries.length > 0 ? (
              <>
                 <ComprehensiveAnalysisView
                   personaSummaries={personaSummaries}
                   finalInsight={finalAnalysis}
                   customAnalysisResults={customAnalysisResults}
                   onAdditionalInterview={() => setShowAdditionalQuestionDialog(true)}
                   loading={loading}
                   forceActiveTab={forceActiveTab}
                   onExportPptx={handleExportPptx}
                   exportingPptx={exportingPptx}
                 />

                {/* 追加質問ダイアログ */}
                {showAdditionalQuestionDialog && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-bold text-gray-900">追加質問インタビュー</h3>
                        <button
                          onClick={() => setShowAdditionalQuestionDialog(false)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>

                      <p className="text-gray-600 mb-6">
                        追加で深掘りしたい質問を入力してください（初期5問、追加可能）
                      </p>

                      {/* Excel アップロード */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                        <h4 className="text-md font-medium text-blue-900 mb-2">Excelファイルから質問を読み込み</h4>
                        <input
                          type="file"
                          accept=".xlsx,.xls"
                          onChange={async (e) => {
                            const file = e.target.files?.[0];
                            if (!file) return;
                            
                            try {
                              setLoading(true);
                              const response = await apiClient.uploadExcelQuestions(file);
                              setAdditionalQuestions(response.questions);
                              alert(`${response.count}個の質問を読み取りました`);
                            } catch (err) {
                              setError('Excelファイルの読み取りに失敗しました');
                            } finally {
                              setLoading(false);
                            }
                          }}
                          disabled={loading}
                          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-600 file:text-white hover:file:bg-blue-700 disabled:opacity-50"
                        />
                      </div>

                      {/* 質問入力フィールド */}
                      <div className="space-y-3 mb-4">
                        {additionalQuestions.map((question, index) => (
                          <div key={index} className="flex items-start space-x-2">
                            <span className="text-sm font-medium text-gray-700 mt-2 min-w-[60px]">
                              質問 {index + 1}
                            </span>
                            <textarea
                              value={question}
                              onChange={(e) => {
                                const newQuestions = [...additionalQuestions];
                                newQuestions[index] = e.target.value;
                                setAdditionalQuestions(newQuestions);
                              }}
                              placeholder="質問内容を入力してください..."
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              rows={2}
                            />
                            {additionalQuestions.length > 1 && (
                              <button
                                onClick={() => {
                                  const newQuestions = additionalQuestions.filter((_, i) => i !== index);
                                  setAdditionalQuestions(newQuestions);
                                }}
                                className="text-red-600 hover:text-red-800 mt-2"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* 質問追加ボタン */}
                      <button
                        onClick={() => setAdditionalQuestions([...additionalQuestions, ''])}
                        className="mb-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 font-medium flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span>質問を追加</span>
                      </button>

                      {/* 実行ボタン */}
                      <div className="flex justify-end space-x-3">
                        <button
                          onClick={() => setShowAdditionalQuestionDialog(false)}
                          className="bg-gray-300 text-gray-700 py-2 px-6 rounded-lg hover:bg-gray-400 font-medium"
                        >
                          キャンセル
                        </button>
                        <button
                          onClick={async () => {
                            try {
                              setLoading(true);
                              setShowAdditionalQuestionDialog(false);
                              setProgress(0);
                              setProgressMessage('追加インタビューを実行中...');

                              const validQuestions = additionalQuestions.filter(q => q.trim());
                              if (validQuestions.length === 0) {
                                setError('有効な質問を入力してください');
                                return;
                              }

                              const newResults: Record<string, InterviewResult[]> = {};
                              const totalPersonas = selectedPersonas.length;

                              for (let i = 0; i < selectedPersonas.length; i++) {
                                setProgress(Math.round((i / totalPersonas) * 100));
                                setProgressMessage(`ペルソナ ${i + 1}/${totalPersonas} の追加インタビュー中...`);

                                const response = await apiClient.conductHypothesisInterview(i, validQuestions);
                                newResults[response.persona_name] = response.interview_results;
                              }

                              setAdditionalInterviewResults(newResults);

                              // personaSummariesを更新
                              const updatedSummaries = personaSummaries.map(summary => ({
                                ...summary,
                                additionalInterview: [
                                  ...(summary.additionalInterview || []),
                                  ...(newResults[summary.personaName] || [])
                                ]
                              }));
                              setPersonaSummaries(updatedSummaries);

                              setProgress(100);
                              setProgressMessage('追加インタビュー完了');
                              
                              // 最初のペルソナのインタビュー詳細タブに遷移
                              setForceActiveTab(0);
                              
                              alert('追加インタビューが完了しました');
                            } catch (err: any) {
                              setError('追加インタビューの実行に失敗しました: ' + (err.response?.data?.detail || err.message));
                            } finally {
                              setLoading(false);
                              setProgress(0);
                              setProgressMessage('');
                            }
                          }}
                          disabled={loading || additionalQuestions.every(q => !q.trim())}
                          className="bg-green-600 text-white py-2 px-6 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                          インタビューを実行
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* アクションボタン */}
                <div className="flex justify-center space-x-4 mt-8">
                  <button
                    onClick={async () => {
                      try {
                        await apiClient.saveInterviewHistory();
                        alert('結果を履歴に保存しました');
                        
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
                      setPersonaSummaries([]);
                      setAdditionalQuestions(['', '', '', '', '']);
                    }}
                    className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 font-medium"
                  >
                    新しいインタビューを開始
                  </button>
                  <button
                    onClick={() => {
                      const element = document.createElement('a');
                      
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
                        `tames interview - 最終レポート\n\n`,
                        `トピック: ${topic}\n\n`,
                        `=== 商品・サービス情報 ===\n${productsInfo}\n`,
                        competitorsInfo,
                        `\n=== 最終マーケティング戦略分析 ===\n${finalAnalysis}\n\n`
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
              </>
            ) : (
              <div className="space-y-8">
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">分析結果</h2>
                  <p className="text-gray-600">
                    インタビュー結果と分析を確認できます
                  </p>
                </div>
                
                <InterviewResults 
                  results={interviewResults} 
                  personas={selectedPersonas}
                />
                
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
            )}
          </div>
        );

      default:
        return null;
    }
  };

  if (loading && step === 0 && connectionStatus === 'connecting') {
    return (
      <div className="flex min-h-screen">
        <Sidebar connectionStatus={connectionStatus} />
        <div className="ml-56 flex flex-1 items-center justify-center">
          <div className="text-center">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-3 border-blue-600 border-t-transparent" />
            <h1 className="text-xl font-semibold text-gray-900 mt-4 mb-1">AI Interview</h1>
            <p className="text-sm text-gray-500">
              {connectionStatus === 'connecting' ? 'サーバーに接続中...' : 'アプリケーションを初期化中...'}
            </p>
            {connectionStatus === 'error' && (
              <div className="mt-4 p-4 rounded-lg border border-red-200 bg-red-50">
                <p className="text-sm text-red-800">{error}</p>
                <button onClick={() => window.location.reload()} className="mt-2 btn-primary text-sm">
                  再読み込み
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[var(--background)]">
      <Sidebar currentStep={step} connectionStatus={connectionStatus} />
      <main className="ml-56 flex-1 py-8 px-6 lg:px-10">
        <div className="max-w-7xl mx-auto">

          {loading && progress > 0 && (
            <div className="mb-6 card p-4">
              <div className="mb-2 flex justify-between items-center">
                <span className="text-sm font-medium text-blue-600">{progressMessage}</span>
                <span className="text-sm text-gray-500">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div 
                  className="h-1.5 rounded-full bg-blue-600 transition-all duration-300 ease-out" 
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {error && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {renderStep()}
        </div>
      </main>
    </div>
  );
}