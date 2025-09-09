// API通信のユーティリティ関数
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

export const apiClient = {
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
  getDefaultQuestions: async (): Promise<{ questions: string[] }> => {
    const response = await api.get('/api/default-questions');
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

  // セッション状態を取得
  getSessionStatus: async () => {
    const response = await api.get('/api/session-status');
    return response.data;
  },
};

export default apiClient;
