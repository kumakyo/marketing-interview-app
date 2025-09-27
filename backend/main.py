# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - FastAPI バックエンド
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import google.generativeai as genai
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

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001"
    ],  # Next.jsの複数ポートに対応
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- APIキーの設定 ---
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("環境変数 'GOOGLE_API_KEY' が設定されていません。")
    genai.configure(api_key=api_key)
except ValueError as e:
    logger.error(f"エラー: {e}")

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

class HistoryRecord(BaseModel):
    id: str
    timestamp: datetime
    project_info: ProjectInfo
    final_analysis: str
    personas_used: List[str]

# --- グローバル変数 ---
current_session = {
    "personas": [],
    "selected_personas": [],
    "interview_sessions": {},
    "total_input_chars": 0,
    "total_output_chars": 0,
    "start_time": time.time(),
    "project_info": None,
    "custom_questions": []
}

# 履歴保存用（実際のプロダクションではデータベースを使用）
interview_history = []

# --- ヘルパー関数 ---
def to_text(text):
    """テキストを整形するヘルパー関数"""
    text = text.replace('•', ' *')
    return textwrap.dedent(text)

def generate_text(prompt, model_name="gemini-pro", temperature=0.8):
    """指定されたプロンプトと設定でテキストを生成する関数"""
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        
        current_session["total_input_chars"] += len(prompt)
        if response.text:
            current_session["total_output_chars"] += len(response.text)
        
        return response.text
    except Exception as e:
        logger.error(f"テキスト生成中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=f"テキスト生成エラー: {e}")

def parse_personas(personas_text):
    """ペルソナテキストを解析する関数"""
    parsed_personas = []
    
    # より柔軟なペルソナ分割（数字や番号で区切る）
    persona_patterns = [
        r'ペルソナ\d+[：:]',
        r'\d+[\.．]\s*ペルソナ',
        r'【ペルソナ\d+】',
        r'■\s*ペルソナ\d+',
        r'^\d+[\.．]',  # 単純な番号
    ]
    
    # ペルソナテキストをより正確に分割
    raw_personas = []
    
    # 改良された正規表現でペルソナブロックを抽出
    persona_pattern = r'ペルソナ(\d+)[：:]?\s*([^\n]+)\n((?:(?!ペルソナ\d+).)*)'
    matches = re.findall(persona_pattern, personas_text, re.DOTALL)
    
    if matches:
        # マッチした場合、ペルソナ番号、名前、詳細を組み合わせる
        for persona_num, persona_name, details in matches:
            persona_block = f"ペルソナ{persona_num}: {persona_name}\n{details.strip()}"
            raw_personas.append(persona_block)
    else:
        # フォールバック: 「ペルソナ」で単純分割
        if 'ペルソナ' in personas_text:
            parts = re.split(r'(?=ペルソナ\d+)', personas_text)
            raw_personas = [p.strip() for p in parts if p.strip() and 'ペルソナ' in p]
        else:
            # 番号で区切る
            parts = re.split(r'\n(?=\d+[\.．])', personas_text)
            raw_personas = [p.strip() for p in parts if p.strip()]
    
    logger.info(f"分割されたペルソナ数: {len(raw_personas)}")
    
    for i, p_text in enumerate(raw_personas):
        # テキストをクリーンアップ（*や不要な文字を除去）
        cleaned_text = re.sub(r'^\*+\s*', '', p_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'\*', '', cleaned_text)
        
        details = {}
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        
        # ペルソナ名を最初の行から抽出
        persona_name = f"ペルソナ{i+1}"
        if lines:
            first_line = lines[0]
            # "ペルソナN: 名前" の形式から名前を抽出
            name_match = re.search(r'ペルソナ\d+[：:]\s*(.+)', first_line)
            if name_match:
                persona_name = name_match.group(1).strip()
        
        # 各行から情報を抽出（より正確に）
        for line in lines:
            if ':' in line or '：' in line:
                separator = ':' if ':' in line else '：'
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # キーから不要な文字を除去
                    key = re.sub(r'^[-•\*\s]+', '', key)
                    
                    # ペルソナ行をスキップ
                    if 'ペルソナ' in key and value == persona_name:
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
                    elif key and value and len(key) < 20:  # 短いキーのみ保存
                        details[key] = value
        
        # ペルソナ名を詳細に追加
        details['ペルソナ名'] = persona_name
        
        # 必要最小限の詳細のみを保持（ただしraw_textも含める）
        filtered_details = {}
        display_keys = ['ペルソナ名', '年齢', '性別', '職業', '年収帯', '居住地', '家族構成', '趣味・余暇', '関心事・悩み']
        
        for key in display_keys:
            if key in details:
                filtered_details[key] = details[key]
        
        # raw_textを詳細情報に含める（フロントエンドで表示用）
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

@app.post("/api/generate-personas")
async def generate_personas(request: PersonaGenerationRequest):
    """ペルソナを生成するエンドポイント"""
    try:
        # セッションにプロジェクト情報を保存
        current_session["project_info"] = request.project_info
        
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
        
        persona_prompt = f"""
        あなたはマーケティングの専門家です。
        以下の商品・サービスと「{request.project_info.topic}」に関するインタビューのための、多様な価値観とライフスタイルを持つ5人のペルソナを作成してください。
        
        【対象商品・サービス情報】
        {products_info}
        
        【競合情報】
        {competitors_info}
        
        各ペルソナについて、以下の詳細を含めてください。厳密にこの形式で出力してください：

        ペルソナ1: [具体的な名前]
        年齢: [年齢]
        性別: [性別]
        職業: [職業]
        年収帯: [年収帯]
        居住地: [居住地]
        家族構成: [家族構成]
        趣味・余暇: [趣味・余暇の過ごし方]
        関心事・悩み: [関心事・主な悩み]

        ペルソナ2: [具体的な名前]
        年齢: [年齢]
        性別: [性別]
        職業: [職業]
        年収帯: [年収帯]
        居住地: [居住地]
        家族構成: [家族構成]
        趣味・余暇: [趣味・余暇の過ごし方]
        関心事・悩み: [関心事・主な悩み]

        ペルソナ3: [具体的な名前]
        年齢: [年齢]
        性別: [性別]
        職業: [職業]
        年収帯: [年収帯]
        居住地: [居住地]
        家族構成: [家族構成]
        趣味・余暇: [趣味・余暇の過ごし方]
        関心事・悩み: [関心事・主な悩み]

        ペルソナ4: [具体的な名前]
        年齢: [年齢]
        性別: [性別]
        職業: [職業]
        年収帯: [年収帯]
        居住地: [居住地]
        家族構成: [家族構成]
        趣味・余暇: [趣味・余暇の過ごし方]
        関心事・悩み: [関心事・主な悩み]

        ペルソナ5: [具体的な名前]
        年齢: [年齢]
        性別: [性別]
        職業: [職業]
        年収帯: [年収帯]
        居住地: [居住地]
        家族構成: [家族構成]
        趣味・余暇: [趣味・余暇の過ごし方]
        関心事・悩み: [関心事・主な悩み]

        注意点：
        - 具体的で現実的な名前を使用してください
        - 上記の商品・サービス情報と「{request.project_info.topic}」に関連する多様な価値観を持つペルソナを作成してください
        - 対象商品・サービスのターゲット顧客層を考慮してペルソナを作成してください
        - 競合商品を知っている、または使用したことがあるペルソナも含めてください
        - アスタリスク（*）や箇条書き記号は使用しないでください
        - 各項目は簡潔に記述してください
        """
        
        personas_text = generate_text(persona_prompt)
        logger.info(f"生成されたペルソナテキスト: {personas_text[:500]}...")
        
        personas = parse_personas(personas_text)
        logger.info(f"パースされたペルソナ数: {len(personas)}")
        
        current_session["personas"] = personas
        current_session["start_time"] = time.time()
        
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
    
    except Exception as e:
        logger.error(f"ペルソナ生成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ペルソナ生成に失敗しました: {e}")

@app.post("/api/select-personas")
async def select_personas(request: PersonaSelectionRequest):
    """ペルソナを選択するエンドポイント"""
    try:
        if not current_session["personas"]:
            raise HTTPException(status_code=400, detail="ペルソナが生成されていません")
        
        if len(request.selected_indices) != 3:
            raise HTTPException(status_code=400, detail="3つのペルソナを選択してください")
        
        selected_personas = [current_session["personas"][i] for i in request.selected_indices]
        current_session["selected_personas"] = selected_personas
        
        # 各ペルソナのチャットセッションを初期化
        model = genai.GenerativeModel('gemini-pro')
        
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
            
            【あなたのペルソナ情報】
            {persona.raw_text}
            
            【調査対象の商品・サービス情報】
            {products_context}
            
            上記の商品・サービスや競合商品について質問された場合は、
            あなたのペルソナの立場から現実的で具体的な回答をしてください。
            
            それでは、インタビューを始めます。準備ができたら「はい、準備ができました」と答えてください。
            """
            
            chat = model.start_chat(history=[
                {'role': 'user', 'parts': [initial_prompt]},
                {'role': 'model', 'parts': ['はい、準備ができました。何でも聞いてください。']}
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
async def get_default_questions(topic: Optional[str] = None):
    """デフォルトの質問リストを取得するエンドポイント"""
    
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
        
        質問は以下の条件を満たしてください：
        - 回答者が対象商品・サービスについて具体的なエピソードを話しやすい設計
        - オープンエンドな質問形式
        - 競合商品・サービスとの比較ができる質問を含める
        - 対象商品・サービスのベネフィットに対する反応を確認できる質問
        - 価格感や購入意向を確認できる質問
        - 自然な会話の流れになるような順番
        - マーケティング戦略立案に有用な洞察が得られる質問
        
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
async def conduct_interview(request: InterviewRequest):
    """インタビューを実行するエンドポイント"""
    try:
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="ペルソナが選択されていません")
        
        persona = current_session["selected_personas"][request.persona_index]
        session = current_session["interview_sessions"][persona.name]
        chat = session["chat"]
        
        interview_results = []
        
        for i, question in enumerate(request.questions):
            # メイン質問
            response = chat.send_message(f"次の質問に回答してください：{question}")
            main_answer = response.text
            
            question_result = {
                "question": question,
                "main_answer": main_answer,
                "follow_ups": []
            }
            
            # 更問を2回実行
            for follow_up_num in range(1, 3):
                follow_up_prompt = f"""
                あなたは優秀なインタビュアーです。これまでの{persona.name}さんとの会話を読んで、
                特に直前の回答について、具体的な行動や感情、潜在的なニーズをさらに深掘りするような、
                1つの簡潔で具体的な質問を作成してください。
                質問は「〇〇について、もう少し詳しく教えていただけますか？」のような対話形式でお願いします。
                
                直前の質問: {question}
                直前の回答: {main_answer}
                """
                
                follow_up_question = generate_text(follow_up_prompt, temperature=0.7)
                
                if follow_up_question and "エラー" not in follow_up_question:
                    try:
                        follow_up_response = chat.send_message(follow_up_question)
                        follow_up_answer = follow_up_response.text
                        
                        question_result["follow_ups"].append({
                            "question": follow_up_question,
                            "answer": follow_up_answer
                        })
                    except Exception as e:
                        logger.error(f"更問への回答生成エラー: {e}")
                        break
            
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
        raise HTTPException(status_code=500, detail=f"インタビューの実行に失敗しました: {e}")

@app.post("/api/generate-analysis")
async def generate_analysis():
    """インサイト分析を生成するエンドポイント"""
    try:
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
        
        【レポート形式】
        1. **対象商品・サービスに対する顧客インサイト**: 各ペルソナの回答から得られた、対象商品・サービスに関する重要な洞察をまとめます。
        2. **競合商品との比較分析**: 競合商品・サービスに対する反応と対象商品の差別化ポイントを分析します。
        3. **ターゲット顧客の検証**: 想定ターゲットと実際のペルソナの反応を比較し、ターゲット設定の妥当性を評価します。
        4. **ベネフィットの受容性**: 提示したベネフィットに対するペルソナの反応を分析し、訴求力を評価します。
        5. **価格感・購入意向**: 価格設定に対する反応と購入意向を分析します。
        6. **マーケティング戦略の示唆**: この分析結果から、具体的なマーケティング戦略を提案します。
        """
        
        analysis_result = generate_text(analysis_prompt)
        
        # コスト計算
        end_time = time.time()
        elapsed_time = end_time - current_session["start_time"]
        estimated_cost = (current_session["total_input_chars"] * INPUT_TOKEN_PRICE) + (current_session["total_output_chars"] * OUTPUT_TOKEN_PRICE)
        
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
        raise HTTPException(status_code=500, detail=f"分析の生成に失敗しました: {e}")

@app.post("/api/generate-hypothesis")
async def generate_hypothesis():
    """初回インタビュー結果から仮説と追加質問を生成するエンドポイント"""
    try:
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
        
        # 初回分析を生成
        all_summaries = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in summaries.items()])
        
        analysis_prompt = f"""
        あなたはトップクラスのマーケティングアナリストです。
        以下の3名のペルソナのインタビュー要約を深く読み解き、詳細なインサイト分析レポートを作成してください。
        
        インタビュー要約:
        {all_summaries}
        
        【レポート形式】
        1. **顧客インサイトの要約**: 各ペルソナの回答から得られた、顧客の心理や行動に関する重要な洞察をまとめます。
        2. **共通点と相違点**: 3名のペルソナ間の回答の共通点と、特に注目すべき相違点を分析します。
        3. **マーケティングの示唆**: この分析結果から、どのようなマーケティング戦略やアプローチが考えられるか、具体的な示唆を記述します。
        4. **未解決の疑問点**: インタビューだけでは明確にならなかった、さらなる調査が必要な点を挙げます。
        """
        
        initial_analysis_result = generate_text(analysis_prompt)
        
        # 仮説と追加質問を生成
        hypothesis_prompt = f"""
        あなたは戦略プランナーです。
        先ほどのインサイト分析レポートを基に、次のアクションに繋がる「マーケティング仮説」と、その仮説を検証するための「追加インタビュー質問」を作成してください。
        
        分析レポート:
        {initial_analysis_result}
        
        【出力形式】
        **マーケティング仮説**:
        - [仮説1]
        - [仮説2]
        - [仮説3]

        **追加インタビュー質問**:
        - [仮説を検証するための質問1]
        - [仮説を検証するための質問2]
        - [仮説を検証するための質問3]
        - [仮説を検証するための質問4]
        - [仮説を検証するための質問5]

        ※追加質問は、仮説検証に特化し、具体的で単一の論点に絞った質問を5個作成してください。
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
                "これまでの仮説について、他に何か深掘りしたい点はありますか？",
                "この商品・サービスに対する期待値について教えてください。",
                "理想的な体験とはどのようなものでしょうか？",
                "現在感じている不満や改善点はありますか？",
                "将来的にどのような変化を期待しますか？"
            ]
        
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
async def conduct_hypothesis_interview(request: InterviewRequest):
    """仮説検証のための追加インタビューを実行するエンドポイント"""
    try:
        if not current_session["selected_personas"]:
            raise HTTPException(status_code=400, detail="ペルソナが選択されていません")
        
        persona = current_session["selected_personas"][request.persona_index]
        session = current_session["interview_sessions"][persona.name]
        chat = session["chat"]
        
        interview_results = []
        
        for i, question in enumerate(request.questions):
            # メイン質問
            response = chat.send_message(f"次の質問に回答してください：{question}")
            main_answer = response.text
            
            question_result = {
                "question": question,
                "main_answer": main_answer,
                "follow_ups": []
            }
            
            # 更問を2回実行
            for follow_up_num in range(1, 3):
                follow_up_prompt = f"""
                あなたは戦略的なインタビュアーです。これまでの{persona.name}さんとの会話履歴を読み、
                提示された仮説を検証するために、直前の回答について、より具体的で洞察的な情報を引き出すような、
                1つの質問を作成してください。
                質問は「〇〇について、どのように感じますか？」のような対話形式でお願いします。
                
                直前の質問: {question}
                直前の回答: {main_answer}
                """
                
                follow_up_question = generate_text(follow_up_prompt, temperature=0.7)
                
                if follow_up_question and "エラー" not in follow_up_question:
                    try:
                        follow_up_response = chat.send_message(follow_up_question)
                        follow_up_answer = follow_up_response.text
                        
                        question_result["follow_ups"].append({
                            "question": follow_up_question,
                            "answer": follow_up_answer
                        })
                    except Exception as e:
                        logger.error(f"更問への回答生成エラー: {e}")
                        break
            
            interview_results.append(question_result)
        
        # セッション履歴を更新
        session["history"].extend(interview_results)
        
        return {
            "persona_name": persona.name,
            "interview_results": interview_results,
            "message": "仮説検証インタビューが完了しました"
        }
    
    except Exception as e:
        logger.error(f"仮説検証インタビュー実行エラー: {e}")
        raise HTTPException(status_code=500, detail=f"仮説検証インタビューの実行に失敗しました: {e}")

@app.post("/api/generate-final-analysis")
async def generate_final_analysis():
    """最終的なマーケティング戦略分析を生成するエンドポイント"""
    try:
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
            以下のペルソナへの全インタビュー内容（初回+仮説検証）を読み、重要なポイントを統合的に要約してください。
            
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
        あなたは経験豊富なCMO（最高マーケティング責任者）です。
        以下のすべての情報（商品・サービス情報、競合情報、ペルソナと全インタビューの結果）を統合し、最終的なマーケティング戦略を策定してください。
        
        {products_context}
        
        全インタビュー要約:
        {all_final_summaries}
        
        【レポート形式】
        1. **商品・サービスの市場適合性**: 対象商品・サービスが市場やペルソナのニーズにどの程度適合しているかを評価します。
        2. **競合優位性の分析**: 競合商品・サービスとの比較から見えてくる差別化ポイントや優位性を分析します。
        3. **ターゲット顧客の精度**: 設定したターゲット顧客とペルソナの反応から、ターゲティングの精度を評価します。
        4. **ベネフィット訴求の効果**: 提示したベネフィットの受容性と説得力を評価し、改善点を提案します。
        5. **価格戦略の妥当性**: 価格設定に対するペルソナの反応から、価格戦略の妥当性を評価します。
        6. **推奨マーケティング戦略**: 上記分析に基づく具体的なマーケティング戦略とアクションプランを提案します。
        7. **リスクと課題**: 予想される課題やリスクとその対策を提案します。
        8. **次のステップ**: 今後実施すべき具体的な施策やさらなる調査項目を提案します。
        """
        
        final_analysis_result = generate_text(final_analysis_prompt)
        
        # コスト計算
        end_time = time.time()
        elapsed_time = end_time - current_session["start_time"]
        estimated_cost = (current_session["total_input_chars"] * INPUT_TOKEN_PRICE) + (current_session["total_output_chars"] * OUTPUT_TOKEN_PRICE)
        
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
async def get_session_status():
    """現在のセッション状態を取得するエンドポイント"""
    return {
        "has_personas": len(current_session["personas"]) > 0,
        "has_selected_personas": len(current_session["selected_personas"]) > 0,
        "selected_persona_count": len(current_session["selected_personas"]),
        "personas": [{"id": i, "name": p.name} for i, p in enumerate(current_session["personas"])],
        "selected_personas": [{"name": p.name} for p in current_session["selected_personas"]],
        "project_info": current_session.get("project_info")
    }

@app.post("/api/upload-excel-questions")
async def upload_excel_questions(file: UploadFile = File(...)):
    """Excelファイルから質問を読み取るエンドポイント"""
    try:
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
async def save_interview_history():
    """インタビュー結果を履歴に保存するエンドポイント"""
    try:
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
            final_analysis=final_analysis_summary,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
