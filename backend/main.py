# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - FastAPI バックエンド
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part
import textwrap
import re
import time
import os
from dotenv import load_dotenv
import logging
import pandas as pd
import json
from datetime import datetime
import uuid
import io

# データベースと認証
from database import get_db, User, Project, Persona, Interview, Analysis, InterviewSessionDB
from auth import get_current_user, get_optional_user, create_or_update_user
from sqlalchemy.orm import Session
import db_manager

# 環境変数を読み込み
load_dotenv()
# プロジェクトルートの.envファイルも読み込み
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(project_root, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションを初期化
app = FastAPI(
    title="マーケティングインタビューシステム",
    description="AI を使ったマーケティングインタビューとインサイト分析システム",
    version="1.0.0"
)

# CORS設定 - 環境変数から許可オリジンを取得
_default_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
_extra_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
if _extra_origins:
    _default_origins.extend([o.strip().rstrip("/") for o in _extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    max_age=3600,
)

# レート制限（グローバル: 1IPあたり60リクエスト/分）
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Vertex AI 初期化 ---
try:
    _gcp_project = os.getenv("GCP_PROJECT_ID", "work-487701")
    _gcp_location = os.getenv("GCP_LOCATION", "asia-northeast1")
    vertexai.init(project=_gcp_project, location=_gcp_location)
    logger.info(f"Vertex AI 初期化完了: project={_gcp_project}, location={_gcp_location}")
except Exception as e:
    logger.error(f"Vertex AI 初期化エラー: {e}")

# --- 料金計算のための定数 ---
INPUT_TOKEN_PRICE = 0.0000007 / 1000
OUTPUT_TOKEN_PRICE = 0.0000021 / 1000

# --- データモデル ---
class ProductService(BaseModel):
    id: str
    name: str
    target_audience: str  # ターゲット顧客
    benefits: str  # ベネフィット
    benefit_reason: str  # ベネフィットを信じられる理由
    basic_info: str  # 価格などの基本情報

class Competitor(BaseModel):
    name: str
    description: str
    price: Optional[str] = None
    features: Optional[str] = None

class ProjectInfo(BaseModel):
    products_services: List[ProductService]
    competitors: List[Competitor]
    topic: str

class PersonaGenerationRequest(BaseModel):
    project_info: ProjectInfo
    persona_count: int = 5  # デフォルト5人
    persona_characteristics: Optional[str] = None  # インタビュー対象者の特徴指定

class PersonaSelectionRequest(BaseModel):
    selected_indices: List[int]

class InterviewRequest(BaseModel):
    persona_index: int
    questions: List[str]
    is_hypothesis_phase: bool = False

class QuestionUploadRequest(BaseModel):
    questions: List[str]

class ChatMessage(BaseModel):
    role: str
    content: str

class Persona(BaseModel):
    name: str
    details: Dict[str, str]
    raw_text: str

class InterviewSession(BaseModel):
    persona: Persona
    chat_history: List[ChatMessage]
    summary: str

class AnalysisTypeRequest(BaseModel):
    analysis_types: List[str]  # ["target_analysis", "improvement_analysis"] の組み合わせ

class HistoryRecord(BaseModel):
    id: str
    timestamp: datetime
    project_info: ProjectInfo
    analysis: str = ""  # 初回分析
    final_analysis: str = ""  # 最終分析
    hypothesis_and_questions: str = ""  # 仮説と質問
    personas_used: List[str]

# --- グローバル変数 ---
# マルチセッション対応: セッションIDをキーとした辞書で管理
sessions = {}

# セッションのデフォルト構造
def create_new_session():
    """新しいセッションを作成する"""
    return {
        "personas": [],
        "selected_personas": [],
        "interview_sessions": {},
        "total_input_chars": 0,
        "total_output_chars": 0,
        "start_time": time.time(),
        "project_info": None,
        "custom_questions": [],
        "analysis_types": [],  # 選択された分析タイプ
        "input_history": {  # 過去の入力履歴
            "products_services": [],
            "competitors": [],
            "topics": []
        }
    }

def get_session(session_id: str):
    """セッションを取得（存在しない場合は作成）"""
    if session_id not in sessions:
        sessions[session_id] = create_new_session()
        logger.info(f"新しいセッションを作成: {session_id}")
    return sessions[session_id]

# 履歴保存用（実際のプロダクションではデータベースを使用）
interview_history = []

# --- ヘルパー関数 ---
def to_text(text):
    """テキストを整形するヘルパー関数"""
    text = text.replace('•', ' *')
    return textwrap.dedent(text)

def generate_text(prompt, model_name="gemini-2.5-flash-lite", temperature=0.8, max_retries=5, session_id=None):
    """Vertex AI でテキストを生成する関数（429 リトライ対応）"""
    if model_name.startswith("models/"):
        model_name = model_name[len("models/"):]

    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            model = GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(temperature=temperature),
            )

            if session_id:
                session = get_session(session_id)
                session["total_input_chars"] += len(prompt)
                if response.text:
                    session["total_output_chars"] += len(response.text)

            return response.text
        except Exception as e:
            last_error = e
            error_message = str(e).lower()

            retryable = (
                "429" in str(e)
                or "overloaded" in error_message
                or "503" in str(e)
                or "504" in str(e)
                or "unavailable" in error_message
                or "timeout" in error_message
                or "resource exhausted" in error_message
                or "quota" in error_message
            )
            if retryable:
                retry_count += 1
                wait_time = min(retry_count * 5, 60)
                logger.warning(f"API一時エラー（リトライ {retry_count}/{max_retries}）: {e}。{wait_time}秒待機中...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"テキスト生成中にエラーが発生しました: {e}")
                raise HTTPException(status_code=500, detail=f"テキスト生成エラー: {e}")

    logger.error(f"テキスト生成が最大リトライ回数（{max_retries}）に達しました: {last_error}")
    raise HTTPException(status_code=503, detail=f"APIが過負荷状態です。しばらく待ってから再試行してください。")

def parse_personas(personas_text):
    """ペルソナテキストを解析する関数"""
    parsed_personas = []
    
    # より柔軟なペルソナ分割パターン
    # 「インタビュー対象者」で始まる行を探す
    persona_pattern = r'(?:インタビュー対象者|ペルソナ)(\d+)[：:]\s*([^\n]+)'
    
    # パターンにマッチする全ての開始位置を見つける
    matches = list(re.finditer(persona_pattern, personas_text))
    
    if not matches:
        logger.warning("ペルソナパターンが見つかりません。テキスト全体を1つのペルソナとして扱います。")
        # フォールバック: テキスト全体を1つのペルソナとして扱う
        matches = [None]
        raw_personas = [personas_text]
    else:
        # 各ペルソナのテキストブロックを抽出
        raw_personas = []
        for i, match in enumerate(matches):
            start_pos = match.start()
            # 次のペルソナの開始位置、または末尾まで
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(personas_text)
            persona_block = personas_text[start_pos:end_pos].strip()
            raw_personas.append(persona_block)
    
    logger.info(f"分割されたペルソナ数: {len(raw_personas)}")
    
    for i, p_text in enumerate(raw_personas):
        # テキストをクリーンアップ
        cleaned_text = re.sub(r'^\*+\s*', '', p_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'\*', '', cleaned_text)
        
        details = {}
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        
        # ペルソナ名を最初の行から抽出
        persona_name = f"ペルソナ{i+1}"
        if lines:
            first_line = lines[0]
            # "インタビュー対象者N: 名前" または "ペルソナN: 名前" の形式から名前を抽出
            name_match = re.search(r'(?:インタビュー対象者|ペルソナ)\d+[：:]\s*(.+)', first_line)
            if name_match:
                persona_name = name_match.group(1).strip()
        
        # 各行から情報を抽出
        for line in lines:
            if ':' in line or '：' in line:
                separator = ':' if ':' in line else '：'
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # キーから不要な文字を除去
                    key = re.sub(r'^[-•\*\s]+', '', key)
                    key = re.sub(r'(?:インタビュー対象者|ペルソナ)\d+\s*', '', key)
                    
                    # ペルソナ行をスキップ
                    if not key or key == persona_name:
                        continue
                    
                    # 特定のキーを標準化
                    if '年齢' in key:
                        details['年齢'] = value
                    elif '性別' in key:
                        details['性別'] = value
                    elif '職業' in key:
                        details['職業'] = value
                    elif '年収' in key:
                        details['年収帯'] = value
                    elif '居住' in key:
                        details['居住地'] = value
                    elif '家族' in key:
                        details['家族構成'] = value
                    elif '趣味' in key or '余暇' in key:
                        details['趣味・余暇'] = value
                    elif '関心' in key or '悩み' in key:
                        details['関心事・悩み'] = value
                    elif key and value and len(key) < 20:
                        details[key] = value
        
        # ペルソナ名を詳細に追加
        details['ペルソナ名'] = persona_name
        
        # 必要最小限の詳細のみを保持
        filtered_details = {}
        display_keys = ['ペルソナ名', '年齢', '性別', '職業', '年収帯', '居住地', '家族構成', '趣味・余暇', '関心事・悩み']
        
        for key in display_keys:
            if key in details:
                filtered_details[key] = details[key]
        
        # raw_textを詳細情報に含める
        filtered_details['raw_text'] = cleaned_text
        
        persona = Persona(
            name=persona_name,
            details=filtered_details,
            raw_text=cleaned_text
        )
        parsed_personas.append(persona)
        
        logger.info(f"ペルソナ{i+1}: {persona_name} - 詳細数: {len(filtered_details)}")
    
    return parsed_personas

# --- API エンドポイント ---

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "マーケティングインタビューシステム API"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """OPTIONSリクエスト（CORSプリフライト）を処理"""
    return {"message": "OK"}

# --- 認証エンドポイント ---

class GoogleSignInRequest(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None

@app.post("/api/auth/google-signin")
async def google_signin(request: GoogleSignInRequest, db: Session = Depends(get_db)):
    """Google認証後のユーザー登録/更新エンドポイント"""
    try:
        user = create_or_update_user(
            user_id=request.id,
            email=request.email,
            name=request.name,
            picture=request.picture,
            db=db
        )
        
        return {
            "message": "ユーザー登録/更新成功",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            }
        }
    except Exception as e:
        logger.error(f"Google認証エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "created_at": current_user.created_at
    }

@app.get("/api/user/projects")
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザーのプロジェクト一覧を取得"""
    try:
        projects = db_manager.get_user_projects(current_user, db, limit=20)
        
        projects_list = []
        for project in projects:
            # 各プロジェクトのペルソナ数とインタビュー数を取得
            personas_count = len(db_manager.get_project_personas(project.id, db))
            interviews_count = len(db_manager.get_project_interviews(project.id, db))
            
            projects_list.append({
                "id": project.id,
                "topic": project.topic,
                "products_count": len(project.products_services) if project.products_services else 0,
                "personas_count": personas_count,
                "interviews_count": interviews_count,
                "created_at": project.created_at.isoformat(),
                "analysis_types": project.analysis_types
            })
        
        return {"projects": projects_list}
    except Exception as e:
        logger.error(f"プロジェクト一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/statistics")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ユーザーの統計情報を取得"""
    try:
        stats = db_manager.get_user_statistics(current_user, db)
        return stats
    except Exception as e:
        logger.error(f"統計情報取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/input-history")
async def get_input_history(session_id: str = "default"):
    """過去の入力履歴を取得するエンドポイント"""
    try:
        session = get_session(session_id)
        return {
            "products_services": session["input_history"]["products_services"][-10:],  # 最新10件
            "competitors": session["input_history"]["competitors"][-10:],
            "topics": session["input_history"]["topics"][-10:]
        }
    except Exception as e:
        logger.error(f"入力履歴取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-psychology")
async def analyze_psychology(
    persona_context: str,
    user_message: str,
    persona_response: str,
    session_id: str = "default"
):
    """発言から深層心理を分析するエンドポイント"""
    try:
        psychology_prompt = f"""
あなたは心理学とマーケティングの専門家です。
以下のインタビュー対象者の発言から、その深層心理（本当は何を考えているか、何を感じているか）を分析してください。

【インタビュー対象者の背景】
{persona_context}

【インタビュアーの質問】
{user_message}

【インタビュー対象者の回答】
{persona_response}

以下の観点から深層心理を分析してください：

1. **表面的な発言の裏にある本音**
   - 言葉では言っていないが、実際には感じているであろうこと
   - 遠慮している、または意識していない潜在的なニーズ

2. **感情的な動機**
   - この発言の背後にある感情（不安、期待、満足、不満など）
   - なぜそのように感じるのか（過去の経験、価値観など）

3. **購買行動への影響**
   - この心理状態が商品・サービスの選択にどう影響するか
   - 意思決定の際に重視する隠れた基準

4. **マーケティング上の示唆**
   - この深層心理から見えるマーケティング機会
   - どのようなアプローチが効果的か

【出力形式】
以下の形式で簡潔に出力してください（各項目100文字以内）：

🧠 本音: [表面的な発言の裏にある本当の気持ち]
💭 感情: [背後にある感情とその理由]
🎯 購買影響: [この心理が購買行動に与える影響]
💡 示唆: [マーケティング上の重要な示唆]
"""
        
        psychology_analysis = generate_text(
            psychology_prompt,
            temperature=0.7,
            session_id=session_id
        )
        
        return {"psychology_analysis": psychology_analysis}
        
    except Exception as e:
        logger.error(f"深層心理分析エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-personas")
async def generate_personas(request: PersonaGenerationRequest, session_id: str = "default"):
    """ペルソナを生成するエンドポイント"""
    try:
        # セッションを取得
        session = get_session(session_id)
        
        # セッションにプロジェクト情報を保存
        session["project_info"] = request.project_info
        
        # 入力履歴に追加（重複を避ける）
        if request.project_info.products_services:
            for product in request.project_info.products_services:
                if product.dict() not in session["input_history"]["products_services"]:
                    session["input_history"]["products_services"].append(product.dict())
        
        if request.project_info.competitors:
            for competitor in request.project_info.competitors:
                if competitor.dict() not in session["input_history"]["competitors"]:
                    session["input_history"]["competitors"].append(competitor.dict())
        
        if request.project_info.topic and request.project_info.topic not in session["input_history"]["topics"]:
            session["input_history"]["topics"].append(request.project_info.topic)
        
        # 商品・サービス情報を含むプロンプトを作成
        products_info = ""
        for product in request.project_info.products_services:
            products_info += f"""
            商品・サービス名: {product.name}
            ターゲット顧客: {product.target_audience}
            ベネフィット: {product.benefits}
            ベネフィットの根拠: {product.benefit_reason}
            基本情報: {product.basic_info}
            """
        
        competitors_info = ""
        if request.project_info.competitors:
            competitors_info = "競合商品・サービス情報:\n"
            for competitor in request.project_info.competitors:
                competitors_info += f"- {competitor.name}: {competitor.description}"
                if competitor.price:
                    competitors_info += f" (価格: {competitor.price})"
                if competitor.features:
                    competitors_info += f" (特徴: {competitor.features})"
                competitors_info += "\n"
        
        # ペルソナの特徴指定がある場合の追加情報
        characteristics_info = ""
        if request.persona_characteristics:
            characteristics_info = f"""
        
        【インタビュー対象者の特徴指定】
        以下の特徴を考慮してインタビュー対象者を作成してください：
        {request.persona_characteristics}
        """

        persona_prompt = f"""
        あなたはマーケティングの専門家です。
        以下の商品・サービスと「{request.project_info.topic}」に関するインタビューのための、多様な価値観とライフスタイルを持つ{request.persona_count}人のインタビュー対象者を作成してください。
        
        【対象商品・サービス情報】
        {products_info}
        
        【競合情報】
        {competitors_info}{characteristics_info}
        
        各インタビュー対象者について、以下の詳細を含めてください。厳密にこの形式で出力してください：

        """ + "\n\n".join([f"""インタビュー対象者{i+1}: [具体的な名前]
        年齢: [年齢]
        性別: [性別]
        職業: [職業]
        年収帯: [年収帯]
        居住地: [居住地]
        家族構成: [家族構成]
        趣味・余暇: [趣味・余暇の過ごし方]
        関心事・悩み: [関心事・主な悩み]""" for i in range(request.persona_count)]) + f"""

        注意点：
        - 具体的で現実的な名前を使用してください
        - 上記の商品・サービス情報と「{request.project_info.topic}」に関連する多様な価値観を持つインタビュー対象者を作成してください
        - 対象商品・サービスのターゲット顧客層を考慮してインタビュー対象者を作成してください
        - 競合商品を知っている、または使用したことがあるインタビュー対象者も含めてください
        - アスタリスク（*）や箇条書き記号は使用しないでください
        - 各項目は簡潔に記述してください
        """
        
        personas_text = generate_text(persona_prompt, session_id=session_id)
        logger.info(f"生成されたペルソナテキスト: {personas_text[:500]}...")
        
        personas = parse_personas(personas_text)
        logger.info(f"パースされたペルソナ数: {len(personas)}")
        
        session["personas"] = personas
        session["start_time"] = time.time()
        
        # レスポンス用のペルソナデータを準備
        persona_list = []
        for i, p in enumerate(personas):
            persona_data = {
                "id": i, 
                "name": p.name, 
                "details": p.details
            }
            logger.info(f"ペルソナ{i}: 名前={p.name}, 詳細キー数={len(p.details)}")
            persona_list.append(persona_data)
        
        return {
            "personas": persona_list,
            "raw_text": personas_text
        }
    
    except HTTPException:
        # HTTPExceptionはそのまま再raiseする
        raise
    except Exception as e:
        logger.error(f"ペルソナ生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ペルソナ生成に失敗しました: {e}")

@app.post("/api/set-analysis-types")
async def set_analysis_types(request: AnalysisTypeRequest, session_id: str = "default"):
    """分析タイプを設定するエンドポイント"""
    try:
        current_session = get_session(session_id)
        current_session["analysis_types"] = request.analysis_types
        return {
            "analysis_types": request.analysis_types,
            "message": "分析タイプが設定されました"
        }
    except Exception as e:
        logger.error(f"分析タイプ設定エラー: {e}")
        raise HTTPException(status_code=500, detail=f"分析タイプの設定に失敗しました: {e}")

@app.post("/api/select-personas")
async def select_personas(request: PersonaSelectionRequest, session_id: str = "default"):
    """ペルソナを選択するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["personas"]:
            raise HTTPException(status_code=400, detail="ペルソナが生成されていません")
        
        if len(request.selected_indices) != 3:
            raise HTTPException(status_code=400, detail="3つのペルソナを選択してください")
        
        selected_personas = [current_session["personas"][i] for i in request.selected_indices]
        current_session["selected_personas"] = selected_personas
        
        # 各ペルソナのチャットセッションを初期化
        model = GenerativeModel("gemini-2.5-flash-lite")
        
        for persona in selected_personas:
            # 商品・サービス情報と競合情報を含むプロンプト
            project_info = current_session.get("project_info")
            products_context = ""
            if project_info:
                for product in project_info.products_services:
                    products_context += f"""
                    調査対象商品・サービス: {product.name}
                    ターゲット: {product.target_audience}
                    ベネフィット: {product.benefits}
                    根拠: {product.benefit_reason}
                    基本情報: {product.basic_info}
                    """
                
                if project_info.competitors:
                    products_context += "\n競合商品・サービス情報:\n"
                    for competitor in project_info.competitors:
                        products_context += f"- {competitor.name}: {competitor.description}"
                        if competitor.price:
                            products_context += f" (価格: {competitor.price})"
                        if competitor.features:
                            products_context += f" (特徴: {competitor.features})"
                        products_context += "\n"
            
            initial_prompt = f"""
            あなたは以下のペルソナになりきり、インタビュアーの質問に答えてください。
            あなたの回答は、ペルソナの性格、価値観、ライフスタイルに沿った、具体的で血の通った内容にしてください。
            回答は簡潔に2-3文程度でまとめ、要点を明確に伝えてください。
            
            【あなたのペルソナ情報】
            {persona.raw_text}
            
            【調査対象の商品・サービス情報】
            {products_context}
            
            上記の商品・サービスや競合商品について質問された場合は、
            あなたのペルソナの立場から現実的で具体的な回答をしてください。
            
            それでは、インタビューを始めます。準備ができたら「はい、準備ができました」と答えてください。
            """
            
            chat = model.start_chat(history=[
                Content(role="user", parts=[Part.from_text(initial_prompt)]),
                Content(role="model", parts=[Part.from_text("はい、準備ができました。何でも聞いてください。")]),
            ])
            
            current_session["interview_sessions"][persona.name] = {
                "persona": persona,
                "chat": chat,
                "summary": "",
                "history": []
            }
        
        return {
            "selected_personas": [{"name": p.name, "details": p.details} for p in selected_personas],
            "message": "ペルソナが選択され、インタビューセッションが初期化されました"
        }
    
    except Exception as e:
        logger.error(f"ペルソナ選択エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ペルソナ選択に失敗しました: {e}")

@app.get("/api/default-questions")
async def get_default_questions(topic: Optional[str] = None, session_id: str = "default"):
    """デフォルトの質問リストを取得するエンドポイント"""
    current_session = get_session(session_id)
    
    # カスタム質問がある場合はそれを返す
    if current_session.get("custom_questions"):
        return {"questions": current_session["custom_questions"]}
    
    # プロジェクト情報に基づく質問プロンプトを作成
    project_info = current_session.get("project_info")
    if project_info and topic:
        # 商品・サービス情報を含むプロンプト
        products_info = ""
        for product in project_info.products_services:
            products_info += f"""
            商品・サービス名: {product.name}
            ターゲット顧客: {product.target_audience}
            ベネフィット: {product.benefits}
            ベネフィットの根拠: {product.benefit_reason}
            基本情報: {product.basic_info}
            """
        
        competitors_info = ""
        if project_info.competitors:
            competitors_info = "競合商品・サービス情報:\n"
            for competitor in project_info.competitors:
                competitors_info += f"- {competitor.name}: {competitor.description}"
                if competitor.price:
                    competitors_info += f" (価格: {competitor.price})"
                if competitor.features:
                    competitors_info += f" (特徴: {competitor.features})"
                competitors_info += "\n"
        
        question_prompt = f"""
        あなたはマーケティングリサーチの専門家です。
        以下の商品・サービスと「{topic}」に関する深掘りマーケティングインタビューで使用する、効果的な質問リストを20個作成してください。
        
        【対象商品・サービス情報】
        {products_info}
        
        【競合情報】
        {competitors_info}
        
        以下の観点を含む質問を作成してください：
        1. 基本情報・ライフスタイル（3-4問）
        2. 「{topic}」と対象商品・サービスに対する現在の利用状況・認識（4-5問）
        3. 競合商品・サービスの利用体験・満足度（3-4問）
        4. 対象商品・サービスのベネフィットに関するニーズ・課題の深掘り（4-5問）
        5. 価格感・購入意向・将来への期待（3-4問）
        6. ネガティブ要因・購入阻害要因の探索（2-3問）
        
        【重要】ネガティブ要因の質問例：
        - この商品・サービスを購入しない理由は何ですか？
        - もしこの商品・サービスを批判するとしたら、どのような点を挙げますか？
        - この商品・サービスに対して不安に感じることはありますか？
        - どのような状況であれば、この商品・サービスを避けたいと思いますか？
        
        質問は以下の条件を満たしてください：
        - 回答者が対象商品・サービスについて具体的なエピソードを話しやすい設計
        - オープンエンドな質問形式
        - 競合商品・サービスとの比較ができる質問を含める
        - 対象商品・サービスのベネフィットに対する反応を確認できる質問
        - 価格感や購入意向を確認できる質問
        - 自然な会話の流れになるような順番
        - マーケティング戦略立案に有用な洞察が得られる質問
        - 質問文には**や[]などの装飾文字は使用せず、シンプルな文章で記載
        - カテゴリ表記は不要、質問文のみを記載
        
        質問例:
        普段、どのような音楽を聴くことが多いですか？
        この商品・サービスに対してどのような印象を持ちますか？
        
        出力形式：
        1. [質問文]
        2. [質問文]
        ...
        20. [質問文]
        """
    elif topic:
        question_prompt = f"""
        あなたはマーケティングリサーチの専門家です。
        「{topic}」に関する深掘りマーケティングインタビューで使用する、効果的な質問リストを20個作成してください。
        
        以下の観点を含む質問を作成してください：
        1. 基本情報・ライフスタイル（3-4問）
        2. 「{topic}」に対する現在の利用状況・認識（4-5問）
        3. 「{topic}」の利用体験・満足度（4-5問）
        4. 「{topic}」に関するニーズ・課題の深掘り（4-5問）
        5. 「{topic}」の感情価値・将来への期待（3-4問）
        
        質問は以下の条件を満たしてください：
        - 回答者が「{topic}」について具体的なエピソードを話しやすい設計
        - オープンエンドな質問形式
        - 「{topic}」に特化した内容で、潜在的なニーズや課題を引き出せる設計
        - 自然な会話の流れになるような順番
        - マーケティング戦略立案に有用な洞察が得られる質問
        
        出力形式：
        1. [質問文]
        2. [質問文]
        ...
        20. [質問文]
        """
    else:
        question_prompt = """
        あなたはマーケティングリサーチの専門家です。
        マーケティングインタビューで使用する、汎用的で効果的な質問リストを20個作成してください。
        
        以下の観点を含む質問を作成してください：
        1. 基本情報・ライフスタイル（3-4問）
        2. 消費行動・価値観（4-5問）
        3. 商品・サービス利用体験（4-5問）
        4. ニーズ・課題の深掘り（4-5問）
        5. 感情・体験価値（3-4問）
        
        質問は以下の条件を満たしてください：
        - 回答者が具体的なエピソードを話しやすい設計
        - オープンエンドな質問形式
        - 特定の商品・サービスに限定しない汎用的な内容
        - 潜在的なニーズや課題を引き出せる設計
        - 自然な会話の流れになるような順番
        
        出力形式：
        1. [質問文]
        2. [質問文]
        ...
        20. [質問文]
        """
    
    try:
        # LLMで質問を生成
        generated_questions_text = generate_text(question_prompt, temperature=0.7)
        
        # 生成されたテキストから質問を抽出
        questions = []
        lines = [line.strip() for line in generated_questions_text.split('\n') if line.strip()]
        
        for line in lines:
            # 番号付きの質問を抽出
            match = re.match(r'^\d+[\.．]\s*(.+)', line)
            if match:
                question = match.group(1).strip()
                questions.append(question)
        
        # 生成に失敗した場合のフォールバック
        if len(questions) < 15:
            logger.warning("LLMでの質問生成が不十分です。デフォルト質問を使用します。")
            questions = [
                "ご自身の簡単な自己紹介（年齢、居住地、職業、家族構成など）をお願いします。",
                "普段の1日の過ごし方について教えてください。",
                "休日の過ごし方について教えてください。どんな人と、どんなことをすることが多いですか？",
                "最近ハマっていること、楽しみにしていることは何ですか？",
                "情報収集はどのような方法で行っていますか？（SNS、ウェブサイト、友人など）",
                "買い物をするときに重視することは何ですか？",
                "外食・レジャー・趣味にどのくらいお金を使いますか？どんな基準で使い先を決めていますか？",
                "新しい商品やサービスを知ったとき、どのような行動を取りますか？",
                "お気に入りのブランドや企業はありますか？その理由は何ですか？",
                "最近購入した商品・サービスで特に満足したものはありますか？",
                "逆に、期待に応えなかった商品・サービスはありますか？どのような点でしょうか？",
                "友人や家族に何かを勧めるときは、どのような基準で判断しますか？",
                "日常生活で困っていることや不便に感じていることはありますか？",
                "理想的な商品・サービスがあるとしたら、どのようなものでしょうか？",
                "価格と品質、どちらを重視しますか？その理由は？",
                "ブランドに対してどのような印象を持ちますか？ブランドは重要ですか？",
                "新しいことを試すのは好きですか？それとも慣れ親しんだものを選びますか？",
                "購入前にどのような情報を調べることが多いですか？",
                "他の人の意見やレビューは購入判断にどの程度影響しますか？",
                "将来的に挑戦したいこと、欲しいものはありますか？"
            ]
        
        # 最大20個に制限
        questions = questions[:20]
        
        logger.info(f"生成された質問数: {len(questions)}")
        return {"questions": questions}
        
    except Exception as e:
        logger.error(f"質問生成エラー: {e}")
        # エラー時のフォールバック
        fallback_questions = [
            "ご自身の簡単な自己紹介（年齢、居住地、職業、家族構成など）をお願いします。",
            "普段の1日の過ごし方について教えてください。",
            "休日の過ごし方について教えてください。どんな人と、どんなことをすることが多いですか？",
            "最近ハマっていること、楽しみにしていることは何ですか？",
            "情報収集はどのような方法で行っていますか？（SNS、ウェブサイト、友人など）",
            "買い物をするときに重視することは何ですか？",
            "外食・レジャー・趣味にどのくらいお金を使いますか？どんな基準で使い先を決めていますか？",
            "新しい商品やサービスを知ったとき、どのような行動を取りますか？",
            "お気に入りのブランドや企業はありますか？その理由は何ですか？",
            "最近購入した商品・サービスで特に満足したものはありますか？",
            "逆に、期待に応えなかった商品・サービスはありますか？どのような点でしょうか？",
            "友人や家族に何かを勧めるときは、どのような基準で判断しますか？",
            "日常生活で困っていることや不便に感じていることはありますか？",
            "理想的な商品・サービスがあるとしたら、どのようなものでしょうか？",
            "価格と品質、どちらを重視しますか？その理由は？",
            "ブランドに対してどのような印象を持ちますか？ブランドは重要ですか？",
            "新しいことを試すのは好きですか？それとも慣れ親しんだものを選びますか？",
            "購入前にどのような情報を調べることが多いですか？",
            "他の人の意見やレビューは購入判断にどの程度影響しますか？",
            "将来的に挑戦したいこと、欲しいものはありますか？"
        ]
        return {"questions": fallback_questions}

@app.post("/api/conduct-interview")
async def conduct_interview(request: InterviewRequest, session_id: str = "default"):
    """インタビューを実行するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="ペルソナが選択されていません")
        
        persona = current_session["selected_personas"][request.persona_index]
        session = current_session["interview_sessions"][persona.name]
        chat = session["chat"]
        
        interview_results = []
        
        for i, question in enumerate(request.questions):
            # メイン質問
            response = chat.send_message(f"次の質問に簡潔に2-3文で回答してください：{question}")
            main_answer = response.text
            
            # メイン回答の深層心理分析
            psychology_analysis = None
            try:
                psychology_prompt = f"""
あなたは心理学とマーケティングの専門家です。
以下のインタビュー対象者の発言から、その深層心理を分析してください。

【インタビュー対象者の背景】
{persona.raw_text}

【質問】{question}
【回答】{main_answer}

以下の観点から簡潔に分析してください（各50-80文字）：

🧠 本音: [表面的な発言の裏にある本当の気持ち]
💭 感情: [背後にある感情とその理由]
🎯 購買影響: [この心理が購買行動に与える影響]
💡 示唆: [マーケティング上の重要な示唆]
"""
                psychology_analysis = generate_text(psychology_prompt, temperature=0.7)
            except Exception as e:
                logger.warning(f"深層心理分析エラー: {e}")
                # エラーが発生してもインタビューは継続
            
            question_result = {
                "question": question,
                "main_answer": main_answer,
                "psychology_analysis": psychology_analysis,
                "follow_ups": []
            }
            
            # 更問を1回実行（時短のため）
            follow_up_prompt = f"""
            あなたは優秀なインタビュアーです。これまでの{persona.name}さんとの会話を読んで、
            特に直前の回答について、具体的な行動や感情、潜在的なニーズをさらに深掘りするような、
            1つの簡潔で具体的な質問を作成してください。
            質問は「〇〇について、もう少し詳しく教えていただけますか？」のような対話形式でお願いします。
            
            直前の質問: {question}
            直前の回答: {main_answer}
            """
            
            try:
                follow_up_question = generate_text(follow_up_prompt, temperature=0.7)
                
                if follow_up_question and "エラー" not in follow_up_question:
                    follow_up_response = chat.send_message(follow_up_question)
                    follow_up_answer = follow_up_response.text
                    
                    question_result["follow_ups"].append({
                        "question": follow_up_question,
                        "answer": follow_up_answer
                    })
            except Exception as e:
                logger.error(f"更問への回答生成エラー: {e}")
                # エラーが発生してもインタビューを継続
            
            interview_results.append(question_result)
        
        # セッション履歴を更新
        session["history"].extend(interview_results)
        
        return {
            "persona_name": persona.name,
            "interview_results": interview_results,
            "message": "インタビューが完了しました"
        }
    
    except Exception as e:
        logger.error(f"インタビュー実行エラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"インタビューの実行に失敗しました: {str(e)}")

@app.post("/api/generate-analysis")
async def generate_analysis(session_id: str = "default"):
    """インサイト分析を生成するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="インタビューデータがありません")
        
        # 各ペルソナのインタビュー要約を作成
        summaries = {}
        for persona in current_session["selected_personas"]:
            session = current_session["interview_sessions"][persona.name]
            history = session["history"]
            
            if not history:
                continue
            
            # インタビュー内容を要約
            interview_content = ""
            for result in history:
                interview_content += f"質問: {result['question']}\n"
                interview_content += f"回答: {result['main_answer']}\n"
                for follow_up in result.get('follow_ups', []):
                    interview_content += f"更問: {follow_up['question']}\n"
                    interview_content += f"更問回答: {follow_up['answer']}\n"
                interview_content += "\n"
            
            summary_prompt = f"""
            以下のペルソナへのインタビュー内容を読み、重要なポイントを簡潔に要約してください。
            
            ペルソナ情報:
            {persona.raw_text}
            
            インタビュー内容:
            {interview_content}
            """
            
            summary = generate_text(summary_prompt, temperature=0.5)
            summaries[persona.name] = summary
        
        # 総合分析を生成
        all_summaries = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in summaries.items()])
        
        # 商品・サービス情報を分析に含める
        project_info = current_session.get("project_info")
        products_context = ""
        if project_info:
            products_context = "\n【対象商品・サービス情報】\n"
            for product in project_info.products_services:
                products_context += f"""
                商品・サービス名: {product.name}
                ターゲット顧客: {product.target_audience}
                ベネフィット: {product.benefits}
                ベネフィットの根拠: {product.benefit_reason}
                基本情報: {product.basic_info}
                """
            
            if project_info.competitors:
                products_context += "\n【競合商品・サービス情報】\n"
                for competitor in project_info.competitors:
                    products_context += f"- {competitor.name}: {competitor.description}"
                    if competitor.price:
                        products_context += f" (価格: {competitor.price})"
                    if competitor.features:
                        products_context += f" (特徴: {competitor.features})"
                    products_context += "\n"
        
        analysis_prompt = f"""
        あなたはトップクラスのマーケティングアナリストです。
        以下の商品・サービス情報と3名のペルソナのインタビュー要約を深く読み解き、詳細なインサイト分析レポートを作成してください。
        
        {products_context}
        
        インタビュー要約:
        {all_summaries}
        
        【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
        
        【レポート形式】（各項目は簡潔に3-4行でまとめてください）
        
        ## 1. ベネフィットへの共感度合い
        - 各ペルソナのベネフィットに対する反応を分析
        - 具体的な発言を根拠として共感度を評価
        
        ## 2. 購買意欲
        - 購入意向の強さとその理由を分析
        - 購入を促進する要因と阻害する要因を特定
        
        ## 3. 購入しない理由の抽出
        - ネガティブ要因や購入阻害要因を詳細に分析
        - 具体的な懸念点や不安要素を整理
        
        ## 4. 回答の裏側にあるインサイトの抽出
        - 表面的な回答の背後にある本音や価値観を分析
        - 隠れたニーズや動機を発見
        
        ## 5. 対象商品・サービスに対する顧客インサイト
        - 各ペルソナの回答から得られた重要な洞察をまとめ
        - 発言内容を根拠として示す
        
        ## 6. 競合商品との比較分析
        - 競合商品・サービスに対する反応と対象商品の差別化ポイントを分析
        - 具体的な比較発言を引用
        
        ## 7. ターゲット顧客の検証
        - 想定ターゲットと実際のペルソナの反応を比較
        - ターゲット設定の妥当性を評価
        
        ## 8. 価格感・購入意向
        - 価格設定に対する反応と購入意向を分析
        - 価格に関する具体的な発言を根拠として提示
        
## 9. 商品・サービス ポジショニングマップ
以下の軸で対象商品・サービスと競合商品を分析し、図示してください：
- 縦軸：顧客満足度（高い/低い）
- 横軸：価格帯（高い/低い）

```
顧客満足度高
　　│
　　│ [高満足・高価格]     [高満足・低価格]
　　│   競合A/対象商品        競合B
────┼────────────────────────
　　│ [低満足・高価格]     [低満足・低価格]
　　│     競合C              競合D
　　│
顧客満足度低     価格帯低     価格帯高
```

各商品・サービスについて、インタビュー結果から判断される位置を示し、
対象商品の競争優位性を分析してください。
        
        ## 10. マーケティング戦略の示唆
        - この分析結果から、具体的なマーケティング戦略を提案
        - 各象限のペルソナに対する具体的なアプローチ方法を記載
        """
        
        analysis_result = generate_text(analysis_prompt)
        
        # コスト計算
        end_time = time.time()
        elapsed_time = end_time - current_session["start_time"]
        estimated_cost = (current_session["total_input_chars"] * INPUT_TOKEN_PRICE) + (current_session["total_output_chars"] * OUTPUT_TOKEN_PRICE)
        
        # 分析結果をセッションに保存
        current_session["analysis"] = analysis_result
        
        return {
            "summaries": summaries,
            "analysis": analysis_result,
            "stats": {
                "elapsed_time": elapsed_time,
                "input_chars": current_session["total_input_chars"],
                "output_chars": current_session["total_output_chars"],
                "estimated_cost": estimated_cost
            }
        }
    
    except Exception as e:
        logger.error(f"分析生成エラー: {e}")
        logger.error(f"セッション状態: selected_personas={len(current_session.get('selected_personas', []))}")
        logger.error(f"プロジェクト情報: {current_session.get('project_info') is not None}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"分析の生成に失敗しました: {str(e)}")

@app.post("/api/generate-hypothesis")
async def generate_hypothesis(session_id: str = "default"):
    """初回インタビュー結果から仮説と追加質問を生成するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="インタビューデータがありません")
        
        # 各ペルソナのインタビュー要約を作成
        summaries = {}
        for persona in current_session["selected_personas"]:
            session = current_session["interview_sessions"][persona.name]
            history = session["history"]
            
            if not history:
                continue
            
            # インタビュー内容を要約
            interview_content = ""
            for result in history:
                interview_content += f"質問: {result['question']}\n"
                interview_content += f"回答: {result['main_answer']}\n"
                for follow_up in result.get('follow_ups', []):
                    interview_content += f"更問: {follow_up['question']}\n"
                    interview_content += f"更問回答: {follow_up['answer']}\n"
                interview_content += "\n"
            
            summary_prompt = f"""
            以下のペルソナへのインタビュー内容を読み、重要なポイントを簡潔に要約してください。
            
            ペルソナ情報:
            {persona.raw_text}
            
            インタビュー内容:
            {interview_content}
            """
            
            summary = generate_text(summary_prompt, temperature=0.5)
            summaries[persona.name] = summary
        
        # 商品・サービス情報と競合情報を取得
        products_context = ""
        if current_session.get("project_info"):
            project_info = current_session["project_info"]
            
            # 商品・サービス情報
            for product in project_info.products_services:
                products_context += f"""
                商品・サービス名: {product.name}
                ターゲット顧客: {product.target_audience}
                ベネフィット: {product.benefits}
                ベネフィットの根拠: {product.benefit_reason}
                基本情報: {product.basic_info}
                """
            
            # 競合情報
            if project_info.competitors:
                products_context += "\n競合商品・サービス情報:\n"
                for competitor in project_info.competitors:
                    products_context += f"- {competitor.name}: {competitor.description}"
                    if competitor.price:
                        products_context += f" (価格: {competitor.price})"
                    if competitor.features:
                        products_context += f" (特徴: {competitor.features})"
                    products_context += "\n"
        
        # 初回分析を生成
        all_summaries = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in summaries.items()])
        
        analysis_prompt = f"""
        あなたはトップクラスのマーケティングアナリストです。
        以下の商品・サービス情報と3名のペルソナのインタビュー要約を深く読み解き、詳細なインサイト分析レポートを作成してください。
        
        【対象商品・サービス情報】
        {products_context}
        
        インタビュー要約:
        {all_summaries}
        
        【レポート形式】（各項目は簡潔に3-4行でまとめてください）
        1. **顧客インサイトの要約**: 各ペルソナの回答から得られた、顧客の心理や行動に関する重要な洞察をまとめます。
        2. **共通点と相違点**: 3名のペルソナ間の回答の共通点と、特に注目すべき相違点を分析します。
        3. **マーケティングの示唆**: この分析結果から、どのようなマーケティング戦略やアプローチが考えられるか、具体的な示唆を記述します。
        4. **未解決の疑問点**: インタビューだけでは明確にならなかった、さらなる調査が必要な点を挙げます。
        """
        
        initial_analysis_result = generate_text(analysis_prompt)
        
        # 仮説と追加質問を生成
        hypothesis_prompt = f"""
        あなたは戦略プランナーです。
        先ほどのインサイト分析レポートを基に、さらに深掘りするための追加質問を作成してください。
        
        分析レポート:
        {initial_analysis_result}
        
        【重要な指示】
        - 質問文は直接的で自然な形で生成してください
        - 「仮説」「検証」などの分析的な文言は一切使用しないでください
        - 各質問は独立した質問として生成してください
        
        **追加インタビュー質問**:
        - [質問内容1]
        - [質問内容2]
        - [質問内容3]
        - [質問内容4]
        - [質問内容5]
        
        質問は以下の観点から生成してください：
        - より具体的な利用シーンや状況について
        - 競合商品との比較や選択理由について
        - 価格感や購入決定要因について
        - 潜在的な不安や懸念事項について
        - 推奨意向や口コミ行動について
        """
        
        hypothesis_and_questions_text = generate_text(hypothesis_prompt)
        
        # 追加質問を抽出
        new_questions_match = re.search(r'追加インタビュー質問[：:]\s*\n(.+)', hypothesis_and_questions_text, re.DOTALL)
        extracted_new_questions = []
        if new_questions_match:
            raw_questions_block = new_questions_match.group(1).strip()
            extracted_new_questions = re.findall(r'^[*-]\s*(.+)', raw_questions_block, re.MULTILINE)
            if not extracted_new_questions:
                extracted_new_questions = re.findall(r'^(?:Q\d+|#\d+|\d+\.|[*-])\s*(.+)', raw_questions_block, re.MULTILINE)
            extracted_new_questions = [q.strip() for q in extracted_new_questions if q.strip()]

        if not extracted_new_questions:
            extracted_new_questions = [
                "これまでの内容について、他に何か深掘りしたい点はありますか？",
                "この商品・サービスに対する期待値について教えてください。",
                "理想的な体験とはどのようなものでしょうか？",
                "現在感じている不満や改善点はありますか？",
                "将来的にどのような変化を期待しますか？"
            ]
        
        # 質問をセッションに保存
        current_session["additional_questions"] = hypothesis_and_questions_text
        
        return {
            "summaries": summaries,
            "initial_analysis": initial_analysis_result,
            "hypothesis_and_questions": hypothesis_and_questions_text,
            "additional_questions": extracted_new_questions
        }
    
    except Exception as e:
        logger.error(f"仮説生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"仮説の生成に失敗しました: {e}")

@app.post("/api/conduct-hypothesis-interview")
async def conduct_hypothesis_interview(request: InterviewRequest, session_id: str = "default"):
    """追加インタビューを実行するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="ペルソナが選択されていません")
        
        persona = current_session["selected_personas"][request.persona_index]
        session = current_session["interview_sessions"][persona.name]
        chat = session["chat"]
        
        interview_results = []
        
        for i, question in enumerate(request.questions):
            # メイン質問
            response = chat.send_message(f"次の質問に簡潔に2-3文で回答してください：{question}")
            main_answer = response.text
            
            question_result = {
                "question": question,
                "main_answer": main_answer,
                "follow_ups": []
            }
            
            # 更問を1回実行（時短のため）
            follow_up_prompt = f"""
            あなたは戦略的なインタビュアーです。これまでの{persona.name}さんとの会話履歴を読み、
            より深い洞察を得るために、直前の回答について、より具体的で洞察的な情報を引き出すような、
            1つの質問を作成してください。
            質問は「〇〇について、どのように感じますか？」のような対話形式でお願いします。
            
            直前の質問: {question}
            直前の回答: {main_answer}
            """
            
            try:
                follow_up_question = generate_text(follow_up_prompt, temperature=0.7)
                
                if follow_up_question and "エラー" not in follow_up_question:
                    follow_up_response = chat.send_message(follow_up_question)
                    follow_up_answer = follow_up_response.text
                    
                    question_result["follow_ups"].append({
                        "question": follow_up_question,
                        "answer": follow_up_answer
                    })
            except Exception as e:
                logger.error(f"更問への回答生成エラー: {e}")
                # エラーが発生してもインタビューを継続
            
            interview_results.append(question_result)
        
        # セッション履歴を更新
        session["history"].extend(interview_results)
        
        return {
            "persona_name": persona.name,
            "interview_results": interview_results,
            "message": "追加インタビューが完了しました"
        }
    
    except Exception as e:
        logger.error(f"追加インタビュー実行エラー: {e}")
        import traceback
        logger.error(f"詳細エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"追加インタビューの実行に失敗しました: {str(e)}")

@app.post("/api/generate-custom-final-analysis")
async def generate_custom_final_analysis(session_id: str = "default"):
    """選択された分析タイプに基づく最終分析を生成するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="インタビューデータがありません")
        
        analysis_types = current_session.get("analysis_types", [])
        if not analysis_types:
            raise HTTPException(status_code=400, detail="分析タイプが選択されていません")
        
        # 全インタビュー結果を要約
        final_summaries = {}
        for persona in current_session["selected_personas"]:
            session = current_session["interview_sessions"][persona.name]
            history = session["history"]
            
            if not history:
                continue
            
            # インタビュー内容を要約
            interview_content = ""
            for result in history:
                interview_content += f"質問: {result['question']}\n"
                interview_content += f"回答: {result['main_answer']}\n"
                for follow_up in result.get('follow_ups', []):
                    interview_content += f"更問: {follow_up['question']}\n"
                    interview_content += f"更問回答: {follow_up['answer']}\n"
                interview_content += "\n"
            
            summary_prompt = f"""
            以下のインタビュー対象者への全インタビュー内容を読み、重要なポイントを統合的に要約してください。
            
            インタビュー対象者情報:
            {persona.raw_text}
            
            全インタビュー内容:
            {interview_content}
            """
            
            summary = generate_text(summary_prompt, temperature=0.5)
            final_summaries[persona.name] = summary
        
        # 選択された分析タイプに基づく分析を生成
        all_final_summaries = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in final_summaries.items()])
        
        # 商品・サービス情報を最終分析に含める
        project_info = current_session.get("project_info")
        products_context = ""
        if project_info:
            products_context = "\n【対象商品・サービス情報】\n"
            for product in project_info.products_services:
                products_context += f"""
                商品・サービス名: {product.name}
                ターゲット顧客: {product.target_audience}
                ベネフィット: {product.benefits}
                ベネフィットの根拠: {product.benefit_reason}
                基本情報: {product.basic_info}
                """
            
            if project_info.competitors:
                products_context += "\n【競合商品・サービス情報】\n"
                for competitor in project_info.competitors:
                    products_context += f"- {competitor.name}: {competitor.description}"
                    if competitor.price:
                        products_context += f" (価格: {competitor.price})"
                    if competitor.features:
                        products_context += f" (特徴: {competitor.features})"
                    products_context += "\n"
        
        # 分析タイプに応じた分析を生成
        analysis_results = {}
        
        if "market_structure" in analysis_types:
            market_analysis_prompt = f"""
            あなたはトップクラスのマーケティングアナリストです。
            以下の商品・サービス情報とインタビュー対象者のインタビュー要約を深く読み解き、
            「市場構造の理解」に焦点を当てた分析を行ってください。
            
            {products_context}
            
            全インタビュー要約:
            {all_final_summaries}
            
            【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
            
            ### 1. 市場全体の動向と構造
            - インタビュー結果から読み取れる市場の現状と傾向
            - 顧客が感じている市場の変化や課題
            
            ### 2. 顧客セグメントの特徴
            - インタビュー対象者から見える顧客セグメントの多様性
            - 各セグメントの特徴的なニーズと行動パターン
            
            ### 3. 競合状況の分析
            - 競合商品・サービスに対する顧客の認識と評価
            - 当社商品・サービスの競争力と差別化ポイント
            
            ### 4. ビジネスチャンスの発見
            - 市場における未充足ニーズや新たな機会
            - 具体的な発言を根拠としたビジネスチャンスの提案
            """
            
            market_analysis = generate_text(market_analysis_prompt)
            analysis_results["market_structure"] = market_analysis
        
        if "customer_needs" in analysis_types:
            customer_needs_analysis_prompt = f"""
            あなたはトップクラスのマーケティングアナリストです。
            以下の商品・サービス情報とインタビュー対象者のインタビュー要約を深く読み解き、
            「特定の消費者ニーズの確認」に焦点を当てた分析を行ってください。
            
            {products_context}
            
            全インタビュー要約:
            {all_final_summaries}
            
            【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
            
            ### 1. 顕在ニーズの深掘り
            - インタビュー対象者が明確に表明しているニーズ
            - 各ニーズの具体的な内容と背景
            
            ### 2. 潜在ニーズの発見
            - 言葉に表れていない潜在的なニーズや期待
            - 回答の裏側にある本音や価値観
            
            ### 3. 商品・サービスとのマッチング分析
            - 対象商品・サービスが満たせるニーズと満たせないニーズ
            - ベネフィットへの共感度とその理由
            
            ### 4. ニーズに基づく推奨アクション
            - 発見されたニーズに応えるための具体的な提案
            - 各顧客セグメントへのアプローチ方法
            """
            
            customer_needs_analysis = generate_text(customer_needs_analysis_prompt)
            analysis_results["customer_needs"] = customer_needs_analysis
        
        if "product_improvement" in analysis_types:
            product_improvement_analysis_prompt = f"""
            あなたはトップクラスのマーケティングアナリストです。
            以下の商品・サービス情報とインタビュー対象者のインタビュー要約を深く読み解き、
            「商品・サービスのブラッシュアップ」に焦点を当てた分析を行ってください。
            
            {products_context}
            
            全インタビュー要約:
            {all_final_summaries}
            
            【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
            
            ### 1. 現状の商品・サービスの評価
            - インタビュー対象者から見た現在の商品・サービスの強みと弱み
            - 具体的な発言を根拠とした評価ポイント
            
            ### 2. 改善すべき具体的なポイント
            - 顧客が感じている不満や不安要素
            - 購入を阻害している具体的な要因
            
            ### 3. 価値提案の最適化
            - より魅力的なベネフィットの伝え方
            - ターゲット顧客に響くメッセージングの提案
            
            ### 4. 具体的な改善アクション
            - 機能・性能面での改善提案
            - 価格戦略、マーケティング戦略の改善提案
            - 優先順位付けと実行計画の示唆
            """
            
            product_improvement_analysis = generate_text(product_improvement_analysis_prompt)
            analysis_results["product_improvement"] = product_improvement_analysis
        
        if "target_analysis" in analysis_types:
            target_analysis_prompt = f"""
            あなたはトップクラスのマーケティングアナリストです。
            以下の商品・サービス情報とインタビュー対象者のインタビュー要約を深く読み解き、
            「商品/サービスが誰に刺さるか？なんで刺さるか？」の分析を行ってください。
            
            {products_context}
            
            全インタビュー要約:
            {all_final_summaries}
            
            【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
            
            ### 1. このサービスは特に誰に刺さるか？
            例）XX代女性の、こういう人。なぜなら、インタビュー対象者のxxx人が「ｘｘｘ」ってコメントをだしているから。などの理由も付与。
            
            ### 2. 刺さる価値は何か？
            例）xxxという価値。理由も付与。
            
            ### 3. その価値をこの人たちに伝えるにはどうすればよいか？
            例）インスタグラムでｘｘｘという広告をｘｘｘ円で出す。等、具体的手法をいくつか提示。
            """
            
            target_analysis = generate_text(target_analysis_prompt)
            analysis_results["target_analysis"] = target_analysis
        
        if "improvement_analysis" in analysis_types:
            improvement_analysis_prompt = f"""
            あなたはトップクラスのマーケティングアナリストです。
            以下の商品・サービス情報とインタビュー対象者のインタビュー要約を深く読み解き、
            「こういう人に刺さるようにするためには今の商品/サービスをどうしたらよいか？」の分析を行ってください。
            
            {products_context}
            
            全インタビュー要約:
            {all_final_summaries}
            
            【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
            
            ### 1. マーケットイン視点：今の市場・顧客のどんな"未充足ニーズ"を満たすべきか？
            
            ### 2. 商品戦略視点：プロダクト/サービスをどう磨くか？
            
            ### 3. マーケティング戦略視点：どのように伝え、広げるか？
            """
            
            improvement_analysis = generate_text(improvement_analysis_prompt)
            analysis_results["improvement_analysis"] = improvement_analysis
        
        # コスト計算
        end_time = time.time()
        elapsed_time = end_time - current_session["start_time"]
        estimated_cost = (current_session["total_input_chars"] * INPUT_TOKEN_PRICE) + (current_session["total_output_chars"] * OUTPUT_TOKEN_PRICE)
        
        # 分析結果をセッションに保存
        current_session["custom_final_analysis"] = analysis_results
        
        return {
            "final_summaries": final_summaries,
            "analysis_results": analysis_results,
            "analysis_types": analysis_types,
            "stats": {
                "elapsed_time": elapsed_time,
                "input_chars": current_session["total_input_chars"],
                "output_chars": current_session["total_output_chars"],
                "estimated_cost": estimated_cost
            }
        }
    
    except Exception as e:
        logger.error(f"カスタム最終分析生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"カスタム最終分析の生成に失敗しました: {e}")

@app.post("/api/generate-final-analysis")
async def generate_final_analysis(session_id: str = "default"):
    """最終的なマーケティング戦略分析を生成するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="インタビューデータがありません")
        
        # 全インタビュー結果を要約
        final_summaries = {}
        for persona in current_session["selected_personas"]:
            session = current_session["interview_sessions"][persona.name]
            history = session["history"]
            
            if not history:
                continue
            
            # インタビュー内容を要約
            interview_content = ""
            for result in history:
                interview_content += f"質問: {result['question']}\n"
                interview_content += f"回答: {result['main_answer']}\n"
                for follow_up in result.get('follow_ups', []):
                    interview_content += f"更問: {follow_up['question']}\n"
                    interview_content += f"更問回答: {follow_up['answer']}\n"
                interview_content += "\n"
            
            summary_prompt = f"""
            以下のペルソナへの全インタビュー内容（初回+追加質問）を読み、重要なポイントを統合的に要約してください。
            
            ペルソナ情報:
            {persona.raw_text}
            
            全インタビュー内容:
            {interview_content}
            """
            
            summary = generate_text(summary_prompt, temperature=0.5)
            final_summaries[persona.name] = summary
        
        # 最終分析を生成
        all_final_summaries = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in final_summaries.items()])
        
        # 商品・サービス情報を最終分析に含める
        project_info = current_session.get("project_info")
        products_context = ""
        if project_info:
            products_context = "\n【対象商品・サービス情報】\n"
            for product in project_info.products_services:
                products_context += f"""
                商品・サービス名: {product.name}
                ターゲット顧客: {product.target_audience}
                ベネフィット: {product.benefits}
                ベネフィットの根拠: {product.benefit_reason}
                基本情報: {product.basic_info}
                """
            
            if project_info.competitors:
                products_context += "\n【競合商品・サービス情報】\n"
                for competitor in project_info.competitors:
                    products_context += f"- {competitor.name}: {competitor.description}"
                    if competitor.price:
                        products_context += f" (価格: {competitor.price})"
                    if competitor.features:
                        products_context += f" (特徴: {competitor.features})"
                    products_context += "\n"
        
        final_analysis_prompt = f"""
        あなたはトップクラスのマーケティングアナリストです。
        以下の商品・サービス情報と3名のペルソナのインタビュー要約を深く読み解き、詳細なインサイト分析レポートを作成してください。
        
        {products_context}
        
        全インタビュー要約:
        {all_final_summaries}
        
        【重要】各分析項目では、必ず具体的な発言内容を根拠として引用し、「〜という発言があることから〜と読み取れる」という形式で記載してください。
        【重要】各項目は必ず「### 数字. 項目名」の形式（ハッシュ3つ）で見出しを付けてください。
        
        【レポート形式】（各項目は詳細に4-5行でまとめてください）
        
        ### 1. ベネフィットへの共感度合い
        各ペルソナのベネフィットに対する反応を分析し、具体的な発言を根拠として共感度を評価してください。
        どのベネフィットが最も響いているか、逆に響いていないベネフィットは何かを明確にしてください。

        ### 2. 購買意欲
        購入意向の強さとその理由を分析し、購入を促進する要因と阻害する要因を特定してください。
        各ペルソナの購買意欲レベルを具体的な発言を根拠として評価してください。

        ### 3. 購入しない理由の抽出
        ネガティブ要因や購入阻害要因を詳細に分析し、具体的な懸念点や不安要素を整理してください。
        価格、機能、信頼性、利便性など、カテゴリ別に阻害要因を分類してください。

        ### 4. 回答の裏側にあるインサイトの抽出
        表面的な回答の背後にある本音や価値観を分析し、隠れたニーズや動機を発見してください。
        言葉に表れない心理的要因や潜在的な課題を具体的に指摘してください。

        ### 5. 対象商品・サービスに対する顧客インサイト
        各ペルソナの回答から得られた重要な洞察をまとめ、発言内容を根拠として示してください。
        顧客の真のニーズと商品・サービスの価値提案のマッチング度を評価してください。

        ### 6. 競合商品との比較分析
        競合商品・サービスに対する反応と対象商品の差別化ポイントを分析してください。
        具体的な比較発言を引用し、競合優位性を明確にしてください。

        ### 7. ターゲット顧客の検証
        想定ターゲットと実際のペルソナの反応を比較し、ターゲット設定の妥当性を評価してください。
        どのペルソナが最も有望な顧客層かを具体的に分析してください。

        ### 8. 価格感・購入意向
        価格設定に対する反応と購入意向を分析し、価格に関する具体的な発言を根拠として提示してください。
        適正価格帯と価格感度を詳細に評価してください。

        ### 9. 顧客セグメント別ヒートマップ（4象限分析）
        以下の軸で各ペルソナと商品・サービスの関係を分析し、テキストで図示してください：
        - 縦軸：購買意欲（高い/低い）
        - 横軸：ベネフィット共感度（高い/低い）

        【4象限分析】
        ■ 高意欲・高共感：[ペルソナ名を記載]
        ■ 高意欲・低共感：[ペルソナ名を記載]
        ■ 低意欲・高共感：[ペルソナ名を記載]
        ■ 低意欲・低共感：[ペルソナ名を記載]

        各象限のペルソナに対する具体的なアプローチ戦略を提案してください。

        ### 10. マーケティング戦略への示唆
        この分析結果から、具体的なマーケティング戦略を提案してください。
        以下の観点から具体的に記載してください：
        - ターゲット顧客層の優先順位
        - 各セグメントへのアプローチ方法
        - 効果的なメッセージング戦略
        - 推奨される販売・マーケティングチャネル
        - 価格戦略の方向性
        """
        
        final_analysis_result = generate_text(final_analysis_prompt)
        
        # コスト計算
        end_time = time.time()
        elapsed_time = end_time - current_session["start_time"]
        estimated_cost = (current_session["total_input_chars"] * INPUT_TOKEN_PRICE) + (current_session["total_output_chars"] * OUTPUT_TOKEN_PRICE)
        
        # 最終分析をセッションに保存
        current_session["final_analysis"] = final_analysis_result
        
        return {
            "final_summaries": final_summaries,
            "final_analysis": final_analysis_result,
            "stats": {
                "elapsed_time": elapsed_time,
                "input_chars": current_session["total_input_chars"],
                "output_chars": current_session["total_output_chars"],
                "estimated_cost": estimated_cost
            }
        }
    
    except Exception as e:
        logger.error(f"最終分析生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"最終分析の生成に失敗しました: {e}")

@app.get("/api/session-status")
async def get_session_status(session_id: str = "default"):
    """現在のセッション状態を取得するエンドポイント"""
    current_session = get_session(session_id)
    return {
        "has_personas": len(current_session["personas"]) > 0,
        "has_selected_personas": len(current_session["selected_personas"]) > 0,
        "selected_persona_count": len(current_session["selected_personas"]),
        "personas": [{"id": i, "name": p.name} for i, p in enumerate(current_session["personas"])],
        "selected_personas": [{"name": p.name} for p in current_session["selected_personas"]],
        "project_info": current_session.get("project_info")
    }

@app.post("/api/upload-excel-questions")
async def upload_excel_questions(file: UploadFile = File(...), session_id: str = "default"):
    """Excelファイルから質問を読み取るエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Excelファイル (.xlsx, .xls) のみ対応しています")
        
        # ファイルを読み取り
        contents = await file.read()
        
        # pandasでExcelファイルを読み取り
        df = pd.read_excel(contents)
        
        # 最初の列から質問を抽出
        questions = []
        for index, row in df.iterrows():
            question = str(row.iloc[0]).strip()
            if question and question != 'nan' and len(question) > 5:
                questions.append(question)
        
        if not questions:
            raise HTTPException(status_code=400, detail="有効な質問が見つかりませんでした")
        
        # セッションに保存
        current_session["custom_questions"] = questions
        
        return {
            "questions": questions,
            "count": len(questions),
            "message": f"{len(questions)}個の質問を読み取りました"
        }
    
    except Exception as e:
        logger.error(f"Excelファイル読み取りエラー: {e}")
        raise HTTPException(status_code=500, detail=f"Excelファイルの読み取りに失敗しました: {e}")

@app.post("/api/save-interview-history")
async def save_interview_history(session_id: str = "default"):
    """インタビュー結果を履歴に保存するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session.get("project_info"):
            raise HTTPException(status_code=400, detail="プロジェクト情報がありません")
        
        # 各ペルソナの全インタビュー結果をまとめて最終分析を生成
        summaries = {}
        for persona in current_session.get("selected_personas", []):
            session = current_session["interview_sessions"].get(persona.name)
            if not session or not session.get("history"):
                continue
            
            # インタビュー内容を要約
            interview_content = ""
            for result in session["history"]:
                interview_content += f"質問: {result['question']}\n"
                interview_content += f"回答: {result['main_answer']}\n"
                for follow_up in result.get('follow_ups', []):
                    interview_content += f"更問: {follow_up['question']}\n"
                    interview_content += f"更問回答: {follow_up['answer']}\n"
                interview_content += "\n"
            
            summaries[persona.name] = interview_content
        
        # 商品・サービス情報と競合情報を含む最終分析
        products_info = ""
        for product in current_session["project_info"].products_services:
            products_info += f"""
            商品・サービス名: {product.name}
            ターゲット顧客: {product.target_audience}
            ベネフィット: {product.benefits}
            ベネフィットの根拠: {product.benefit_reason}
            基本情報: {product.basic_info}
            """
        
        competitors_info = ""
        if current_session["project_info"].competitors:
            competitors_info = "\n競合商品・サービス情報:\n"
            for competitor in current_session["project_info"].competitors:
                competitors_info += f"- {competitor.name}: {competitor.description}"
                if competitor.price:
                    competitors_info += f" (価格: {competitor.price})"
                if competitor.features:
                    competitors_info += f" (特徴: {competitor.features})"
                competitors_info += "\n"
        
        final_analysis_summary = f"""
        プロジェクト概要:
        トピック: {current_session["project_info"].topic}
        
        商品・サービス情報:
        {products_info}
        {competitors_info}
        
        インタビュー実施ペルソナ: {', '.join(summaries.keys())}
        """
        
        history_record = HistoryRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            project_info=current_session["project_info"],
            analysis=current_session.get("analysis", ""),  # 初回分析を保存
            final_analysis=current_session.get("final_analysis", final_analysis_summary),  # 最終分析を保存
            hypothesis_and_questions=current_session.get("hypothesis_and_questions", ""),  # 仮説と質問を保存
            personas_used=[p.name for p in current_session.get("selected_personas", [])]
        )
        
        interview_history.append(history_record)
        
        return {
            "message": "履歴に保存しました",
            "history_id": history_record.id
        }
    
    except Exception as e:
        logger.error(f"履歴保存エラー: {e}")
        raise HTTPException(status_code=500, detail=f"履歴の保存に失敗しました: {e}")

@app.get("/api/interview-history")
async def get_interview_history():
    """過去のインタビュー履歴を取得するエンドポイント"""
    try:
        history_list = []
        for record in interview_history:
            history_list.append({
                "id": record.id,
                "timestamp": record.timestamp,
                "topic": record.project_info.topic,
                "products_count": len(record.project_info.products_services),
                "personas_used": record.personas_used
            })
        
        # 新しい順にソート
        history_list.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"history": history_list}
    
    except Exception as e:
        logger.error(f"履歴取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"履歴の取得に失敗しました: {e}")

@app.get("/api/interview-history/{history_id}")
async def get_interview_history_detail(history_id: str):
    """特定の履歴詳細を取得するエンドポイント"""
    try:
        for record in interview_history:
            if record.id == history_id:
                return {
                    "id": record.id,
                    "timestamp": record.timestamp,
                    "project_info": record.project_info,
                    "final_analysis": record.final_analysis,
                    "personas_used": record.personas_used
                }
        
        raise HTTPException(status_code=404, detail="履歴が見つかりませんでした")
    
    except Exception as e:
        logger.error(f"履歴詳細取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"履歴詳細の取得に失敗しました: {e}")

@app.post("/api/generate-interview-summary")
async def generate_interview_summary(session_id: str = "default"):
    """各ペルソナのインタビュー結果からサマリを生成するエンドポイント"""
    try:
        current_session = get_session(session_id)
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="インタビューデータがありません")
        
        summaries = []
        
        for persona in current_session["selected_personas"]:
            session = current_session["interview_sessions"].get(persona.name)
            if not session or not session.get("history"):
                continue
            
            # インタビュー内容を整理（発言と深層心理を含める）
            interview_content = ""
            key_quotes = []  # 重要な発言を収集
            psychology_insights = []  # 深層心理の洞察を収集
            
            for result in session["history"]:
                interview_content += f"質問: {result['question']}\n"
                interview_content += f"回答: {result['main_answer']}\n"
                
                # 重要な発言として保存
                key_quotes.append({
                    "question": result['question'],
                    "answer": result['main_answer']
                })
                
                # 深層心理があれば追加
                if result.get('psychology_analysis'):
                    interview_content += f"深層心理分析: {result['psychology_analysis']}\n"
                    psychology_insights.append(result['psychology_analysis'])
                
                for follow_up in result.get('follow_ups', []):
                    interview_content += f"更問: {follow_up['question']}\n"
                    interview_content += f"更問回答: {follow_up['answer']}\n"
                    
                    # フォローアップの深層心理があれば追加
                    if follow_up.get('psychology_analysis'):
                        interview_content += f"深層心理分析: {follow_up['psychology_analysis']}\n"
                        psychology_insights.append(follow_up['psychology_analysis'])
                
                interview_content += "\n"
            
            # LLMでサマリを生成（深層心理と根拠を統合）
            summary_prompt = f"""
            以下のペルソナへのインタビュー内容を読み、深層心理分析を踏まえて包括的なサマリを作成してください：
            
            1. **結論**: このペルソナのインタビューから得られた最も重要な結論を3-4行で明確に記述
            2. **根拠となる発言**: 結論を裏付ける具体的な発言を2-3つ引用（「〜」という発言）
            3. **深層心理**: 発言の裏にある深層心理や本音を2-3行で分析
            4. **マーケティング示唆**: 上記を踏まえた具体的なマーケティング戦略を3-4行で提示
            
            ペルソナ情報:
            {persona.raw_text}
            
            インタビュー内容（発言と深層心理分析を含む）:
            {interview_content}
            
            出力形式:
            【結論】
            [最も重要な結論を3-4行で明確に]
            
            【根拠となる発言】
            • 「[具体的な発言1]」
            • 「[具体的な発言2]」
            • 「[具体的な発言3]」（オプション）
            
            【深層心理】
            [発言の裏にある本音や感情を2-3行で]
            
            【マーケティング示唆】
            [具体的な戦略やアプローチを3-4行で]
            """
            
            summary_text = generate_text(summary_prompt, temperature=0.6)
            
            # サマリをパース（新形式対応）
            conclusion = ""
            evidence = ""
            psychology = ""
            implications = ""
            
            if "【結論】" in summary_text:
                parts = summary_text.split("【結論】")[1]
                if "【根拠となる発言】" in parts:
                    conclusion = parts.split("【根拠となる発言】")[0].strip()
                    parts = parts.split("【根拠となる発言】")[1]
                    
                    if "【深層心理】" in parts:
                        evidence = parts.split("【深層心理】")[0].strip()
                        parts = parts.split("【深層心理】")[1]
                        
                        if "【マーケティング示唆】" in parts:
                            psychology = parts.split("【マーケティング示唆】")[0].strip()
                            implications = parts.split("【マーケティング示唆】")[1].strip()
            
            # レスポンス用に整形
            formatted_summary = f"""
【結論】
{conclusion}

【根拠となる発言】
{evidence}

【深層心理】
{psychology}

【マーケティング示唆】
{implications}
""".strip()
            
            summaries.append({
                "persona_name": persona.name,
                "main_findings": conclusion,  # 後方互換性のため
                "main_implications": implications,  # 後方互換性のため
                "full_summary": formatted_summary,  # 新しい完全なサマリ
                "evidence": evidence,  # 根拠となる発言
                "psychology": psychology  # 深層心理
            })
        
        return {"summaries": summaries}
    
    except Exception as e:
        logger.error(f"インタビューサマリ生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"インタビューサマリの生成に失敗しました: {e}")

from fastapi.responses import StreamingResponse
import pptx_generator


class ExportPptxRequest(BaseModel):
    session_id: str = "default"
    include_final_analysis: bool = True
    include_custom_analysis: bool = True


@app.post("/api/export-pptx")
async def export_pptx(request: ExportPptxRequest):
    """マーケティングインサイトレポートをPowerPointとしてエクスポート"""
    try:
        current_session = get_session(request.session_id)

        project_info = current_session.get("project_info")
        if not project_info:
            raise HTTPException(status_code=400, detail="プロジェクト情報がありません")

        topic = project_info.topic if hasattr(project_info, "topic") else str(project_info)
        products = []
        if hasattr(project_info, "products_services"):
            products = [p.dict() if hasattr(p, "dict") else p for p in project_info.products_services]

        personas_data = []
        for p in current_session.get("selected_personas", current_session.get("personas", [])):
            if hasattr(p, "name"):
                personas_data.append({"name": p.name, "details": p.details})
            elif isinstance(p, dict):
                personas_data.append(p)

        analysis_text = current_session.get("analysis", "")
        final_analysis = current_session.get("final_analysis", "") if request.include_final_analysis else None
        custom_analysis = current_session.get("custom_final_analysis", None) if request.include_custom_analysis else None

        # LLMでプレゼンターノートを生成
        presenter_notes = None
        if analysis_text:
            try:
                notes_prompt = f"""以下のマーケティング分析結果から、プレゼンター向けの説明メモを200文字以内で簡潔に作成してください。
重要なポイントと話すべきハイライトをまとめてください。

分析結果:
{analysis_text[:1500]}
"""
                presenter_notes = generate_text(notes_prompt, temperature=0.5, session_id=request.session_id)
            except Exception:
                logger.warning("プレゼンターノート生成をスキップ")

        pptx_bytes = pptx_generator.generate_report(
            topic=topic,
            products=products,
            personas=personas_data,
            analysis_text=analysis_text,
            custom_analysis=custom_analysis,
            final_analysis=final_analysis,
            presenter_notes=presenter_notes,
        )

        filename = f"tames_insight_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"

        return StreamingResponse(
            io.BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PPTX生成エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"レポート生成に失敗しました: {e}")


if __name__ == "__main__":
    import uvicorn
    import os
    
    # SSL証明書のパスを設定
    cert_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certs", "cert.pem")
    key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "certs", "key.pem")
    
    # SSL証明書が存在する場合はHTTPSで起動、そうでない場合はHTTPで起動
    if os.path.exists(cert_file) and os.path.exists(key_file):
        logger.info("🔐 HTTPSモードで起動します")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            ssl_keyfile=key_file,
            ssl_certfile=cert_file
        )
    else:
        logger.warning("⚠️ SSL証明書が見つかりません。HTTPモードで起動します")
        logger.warning(f"証明書ファイル: {cert_file}")
        logger.warning(f"秘密鍵ファイル: {key_file}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
