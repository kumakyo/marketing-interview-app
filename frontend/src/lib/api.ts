// API通信のユーティリティ関数
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // timeout機能を削除（インタビュー実行時に無制限の時間を許可）
});

export interface Persona {
  id: number;
  name: string;
  details: Record<string, string>;
}

export interface PersonaGenerationResponse {
  personas: Persona[];
  raw_text: string;
}

export interface InterviewResult {
  question: string;
  main_answer: string;
  follow_ups: {
    question: string;
    answer: string;
  }[];
}

export interface InterviewResponse {
  persona_name: string;
  interview_results: InterviewResult[];
  message: string;
}

export interface AnalysisResponse {
  summaries: Record<string, string>;
  analysis: string;
  stats: {
    elapsed_time: number;
    input_chars: number;
    output_chars: number;
    estimated_cost: number;
  };
}

export interface HypothesisResponse {
  summaries: Record<string, string>;
  initial_analysis: string;
  hypothesis_and_questions: string;
  additional_questions: string[];
}

export interface FinalAnalysisResponse {
  final_summaries: Record<string, string>;
  final_analysis: string;
  stats: {
    elapsed_time: number;
    input_chars: number;
    output_chars: number;
    estimated_cost: number;
  };
}

export const apiClient = {
  // API接続テスト（短いタイムアウトを設定）
  testConnection: async (): Promise<{ status: string; message: string }> => {
    try {
      const response = await api.get('/', { timeout: 5000 }); // 5秒のタイムアウト
      return { status: 'success', message: 'API接続成功' };
    } catch (error: any) {
      console.error('API接続エラー:', error);
      if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        return { status: 'error', message: 'バックエンドサーバーに接続できません。サーバーが起動していることを確認してください。' };
      } else if (error.timeout || error.code === 'ECONNABORTED') {
        return { status: 'error', message: 'API接続がタイムアウトしました。' };
      } else {
        return { status: 'error', message: `API接続エラー: ${error.message}` };
      }
    }
  },

  // ペルソナを生成
  generatePersonas: async (topic: string): Promise<PersonaGenerationResponse> => {
    const response = await api.post('/api/generate-personas', { topic });
    return response.data;
  },

  // ペルソナを選択
  selectPersonas: async (selectedIndices: number[]) => {
    const response = await api.post('/api/select-personas', { selected_indices: selectedIndices });
    return response.data;
  },

  // デフォルトの質問を取得
  getDefaultQuestions: async (topic?: string): Promise<{ questions: string[] }> => {
    const params = topic ? { topic } : {};
    const response = await api.get('/api/default-questions', { params });
    return response.data;
  },

  // インタビューを実行
  conductInterview: async (personaIndex: number, questions: string[], isHypothesisPhase = false): Promise<InterviewResponse> => {
    const response = await api.post('/api/conduct-interview', {
      persona_index: personaIndex,
      questions,
      is_hypothesis_phase: isHypothesisPhase,
    });
    return response.data;
  },

  // 分析を生成
  generateAnalysis: async (): Promise<AnalysisResponse> => {
    const response = await api.post('/api/generate-analysis');
    return response.data;
  },

  // 仮説と追加質問を生成
  generateHypothesis: async (): Promise<HypothesisResponse> => {
    const response = await api.post('/api/generate-hypothesis');
    return response.data;
  },

  // 仮説検証インタビューを実行
  conductHypothesisInterview: async (personaIndex: number, questions: string[]): Promise<InterviewResponse> => {
    const response = await api.post('/api/conduct-hypothesis-interview', {
      persona_index: personaIndex,
      questions,
      is_hypothesis_phase: true,
    });
    return response.data;
  },

  // 最終分析を生成
  generateFinalAnalysis: async (): Promise<FinalAnalysisResponse> => {
    const response = await api.post('/api/generate-final-analysis');
    return response.data;
  },

  // セッション状態を取得
  getSessionStatus: async () => {
    const response = await api.get('/api/session-status');
    return response.data;
  },
};

export default apiClient;
