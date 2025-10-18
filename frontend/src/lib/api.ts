// API通信のユーティリティ関数
import axios from 'axios';

// 外部アクセス用のAPI URLを動的に決定
const getApiBaseUrl = () => {
  // ブラウザ環境でのみ実行
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // 環境変数が設定されている場合はそれを優先
    if (process.env.NEXT_PUBLIC_API_URL) {
      return process.env.NEXT_PUBLIC_API_URL;
    }
    
    // ローカルホストの場合
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    } else {
      // 外部アクセスの場合は同じホスト名でポート8000を使用
      return `${protocol}//${hostname}:8000`;
    }
  }
  
  // サーバーサイドレンダリング時はデフォルト値
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5分のタイムアウト（LLM処理のため長めに設定）
  withCredentials: false, // CORS対応
});

// デバッグ用: API接続情報をコンソールに出力
if (typeof window !== 'undefined') {
  console.log('🔗 API Base URL:', API_BASE_URL);
  console.log('🌐 Current hostname:', window.location.hostname);
}

export interface ProductService {
  id: string;
  name: string;
  target_audience: string;
  benefits: string;
  benefit_reason: string;
  basic_info: string;
}

export interface Competitor {
  name: string;
  description: string;
  price?: string;
  features?: string;
}

export interface ProjectInfo {
  products_services: ProductService[];
  competitors: Competitor[];
  topic: string;
}

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

export interface CustomFinalAnalysisResponse {
  final_summaries: Record<string, string>;
  analysis_results: Record<string, string>;
  analysis_types: string[];
  stats: {
    elapsed_time: number;
    input_chars: number;
    output_chars: number;
    estimated_cost: number;
  };
}

export const apiClient = {
  // API接続テスト（長めのタイムアウトを設定）
  testConnection: async (): Promise<{ status: string; message: string }> => {
    try {
      const response = await api.get('/', { timeout: 60000 }); // 60秒のタイムアウト
      return { status: 'success', message: 'API接続成功' };
    } catch (error: any) {
      console.error('API接続エラー:', error);
      console.error('エラー詳細:', {
        code: error.code,
        message: error.message,
        response: error.response?.status,
        baseURL: API_BASE_URL
      });
      
      if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        return { status: 'error', message: `バックエンドサーバー(${API_BASE_URL})に接続できません。サーバーが起動していることを確認してください。` };
      } else if (error.timeout || error.code === 'ECONNABORTED') {
        return { status: 'error', message: `API接続がタイムアウトしました(${API_BASE_URL})。ネットワーク接続を確認してください。` };
      } else if (error.response) {
        return { status: 'error', message: `APIエラー(${error.response.status}): ${error.message}` };
      } else if (error.request) {
        return { status: 'error', message: `ネットワークエラー: サーバー(${API_BASE_URL})に接続できません。ファイアウォールやネットワーク設定を確認してください。` };
      } else {
        return { status: 'error', message: `API接続エラー: ${error.message}` };
      }
    }
  },

  // ペルソナを生成
  generatePersonas: async (
    projectInfo: ProjectInfo, 
    personaCount: number = 5, 
    personaCharacteristics?: string
  ): Promise<PersonaGenerationResponse> => {
    const response = await api.post('/api/generate-personas', { 
      project_info: projectInfo,
      persona_count: personaCount,
      persona_characteristics: personaCharacteristics
    });
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

  // 分析タイプを設定
  setAnalysisTypes: async (analysisTypes: string[]): Promise<{ analysis_types: string[]; message: string }> => {
    const response = await api.post('/api/set-analysis-types', { analysis_types: analysisTypes });
    return response.data;
  },

  // カスタム最終分析を生成
  generateCustomFinalAnalysis: async (): Promise<CustomFinalAnalysisResponse> => {
    const response = await api.post('/api/generate-custom-final-analysis');
    return response.data;
  },

  // セッション状態を取得
  getSessionStatus: async () => {
    const response = await api.get('/api/session-status');
    return response.data;
  },

  // Excelファイルから質問をアップロード
  uploadExcelQuestions: async (file: File): Promise<{ questions: string[]; count: number; message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/upload-excel-questions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // インタビュー履歴を保存
  saveInterviewHistory: async (): Promise<{ message: string; history_id: string }> => {
    const response = await api.post('/api/save-interview-history');
    return response.data;
  },

  // インタビュー履歴一覧を取得
  getInterviewHistory: async (): Promise<{ history: any[] }> => {
    const response = await api.get('/api/interview-history');
    return response.data;
  },

  // 特定の履歴詳細を取得
  getInterviewHistoryDetail: async (historyId: string): Promise<any> => {
    const response = await api.get(`/api/interview-history/${historyId}`);
    return response.data;
  },

  // インタビューサマリを生成
  generateInterviewSummary: async (): Promise<{ 
    summaries: {
      persona_name: string;
      main_findings: string;
      main_implications: string;
    }[] 
  }> => {
    const response = await api.post('/api/generate-interview-summary');
    return response.data;
  },
};

export default apiClient;
