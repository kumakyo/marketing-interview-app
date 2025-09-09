'use client';

import React, { useState, useEffect } from 'react';
import { apiClient, Persona, InterviewResult } from '@/lib/api';
import PersonaCard from '@/components/PersonaCard';
import InterviewCard from '@/components/InterviewCard';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function Home() {
  const [step, setStep] = useState(1);
  const [topic, setTopic] = useState('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersonas, setSelectedPersonas] = useState<number[]>([]);
  const [questions, setQuestions] = useState<string[]>([]);
  const [interviewResults, setInterviewResults] = useState<Record<string, InterviewResult[]>>({});
  const [analysis, setAnalysis] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // デフォルトの質問を読み込み
    const loadDefaultQuestions = async () => {
      try {
        const response = await apiClient.getDefaultQuestions();
        setQuestions(response.questions);
      } catch (err) {
        console.error('デフォルト質問の読み込みに失敗しました:', err);
      }
    };
    loadDefaultQuestions();
  }, []);

  const handleGeneratePersonas = async () => {
    if (!topic.trim()) {
      setError('トピックを入力してください');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await apiClient.generatePersonas(topic);
      setPersonas(response.personas);
      setStep(2);
    } catch (err: any) {
      setError('ペルソナの生成に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
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

    try {
      await apiClient.selectPersonas(selectedPersonas);
      setStep(3);
    } catch (err: any) {
      setError('ペルソナの選択に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleConductInterview = async () => {
    setLoading(true);
    setError('');

    try {
      const results: Record<string, InterviewResult[]> = {};
      
      for (let i = 0; i < selectedPersonas.length; i++) {
        const response = await apiClient.conductInterview(i, questions);
        results[response.persona_name] = response.interview_results;
      }
      
      setInterviewResults(results);
      setStep(4);
    } catch (err: any) {
      setError('インタビューの実行に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAnalysis = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await apiClient.generateAnalysis();
      setAnalysis(response.analysis);
      setStep(5);
    } catch (err: any) {
      setError('分析の生成に失敗しました: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                マーケティングインタビューシステム
              </h1>
              <p className="text-lg text-gray-600 mb-8">
                AIを活用してペルソナを生成し、深掘りインタビューでインサイトを発見します
              </p>
            </div>
            
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
              
              <button
                onClick={handleGeneratePersonas}
                disabled={loading || !topic.trim()}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
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
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {personas.map((persona) => (
                <PersonaCard
                  key={persona.id}
                  persona={persona}
                  isSelected={selectedPersonas.includes(persona.id)}
                  onSelect={handlePersonaSelection}
                />
              ))}
            </div>
            
            <div className="flex justify-center">
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
            
            <div className="space-y-4">
              {questions.map((question, index) => (
                <div key={index} className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    質問 {index + 1}
                  </label>
                  <textarea
                    value={question}
                    onChange={(e) => {
                      const newQuestions = [...questions];
                      newQuestions[index] = e.target.value;
                      setQuestions(newQuestions);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={2}
                  />
                </div>
              ))}
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleConductInterview}
                disabled={loading}
                className="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? <LoadingSpinner size="sm" text="インタビューを実行中..." /> : 'インタビューを実行'}
              </button>
            </div>
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
                {loading ? <LoadingSpinner size="sm" text="分析を生成中..." /> : 'インサイト分析を生成'}
              </button>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">インサイト分析結果</h2>
              <p className="text-gray-600">
                AIによる総合的なマーケティングインサイト分析
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
                onClick={() => {
                  setStep(1);
                  setTopic('');
                  setPersonas([]);
                  setSelectedPersonas([]);
                  setInterviewResults({});
                  setAnalysis('');
                }}
                className="bg-blue-600 text-white py-3 px-8 rounded-lg hover:bg-blue-700 font-medium"
              >
                新しいインタビューを開始
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* プログレスバー */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            {[1, 2, 3, 4, 5].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    step >= stepNumber
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {stepNumber}
                </div>
                {stepNumber < 5 && (
                  <div
                    className={`w-16 h-1 ${
                      step > stepNumber ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-2">
            <span className="text-sm text-gray-600">
              ステップ {step} / 5
            </span>
          </div>
        </div>

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