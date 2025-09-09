# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - FastAPI バックエンド
"""

from fastapi import FastAPI, HTTPException
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

# 環境変数を読み込み
load_dotenv()

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
    allow_origins=["http://localhost:3000"],  # Next.jsのデフォルトポート
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
class PersonaGenerationRequest(BaseModel):
    topic: str

class PersonaSelectionRequest(BaseModel):
    selected_indices: List[int]

class InterviewRequest(BaseModel):
    persona_index: int
    questions: List[str]
    is_hypothesis_phase: bool = False

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

# --- グローバル変数 ---
current_session = {
    "personas": [],
    "selected_personas": [],
    "interview_sessions": {},
    "total_input_chars": 0,
    "total_output_chars": 0,
    "start_time": time.time()
}

# --- ヘルパー関数 ---
def to_text(text):
    """テキストを整形するヘルパー関数"""
    text = text.replace('•', ' *')
    return textwrap.dedent(text)

def generate_text(prompt, model_name="models/gemini-1.5-flash", temperature=0.8):
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
    raw_personas = [p.strip() for p in personas_text.split('ペルソナ') if p.strip()]
    
    for i, p_text in enumerate(raw_personas):
        details = {'raw_text': p_text}
        lines = p_text.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                details[key.strip()] = value.strip()
        
        if 'ペルソナ名' not in details:
            name_match = re.search(r'ペルソナ\d+:\s*(.+)', lines[0] if lines else "")
            details['ペルソナ名'] = name_match.group(1).strip() if name_match else f"ペルソナ{i+1}"
        
        persona = Persona(
            name=details.get('ペルソナ名', f'ペルソナ{i+1}'),
            details=details,
            raw_text=p_text
        )
        parsed_personas.append(persona)
    
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
        persona_prompt = f"""
        あなたはマーケティングの専門家です。
        「{request.topic}」に関するインタビューのための、多様な価値観とライフスタイルを持つ5人のペルソナを作成してください。
        各ペルソナについて、以下の詳細を含めてください。
        - ペルソナ名
        - 年齢
        - 性別
        - 職業
        - 年収帯
        - 居住地
        - 家族構成
        - 趣味・余暇の過ごし方
        - 関心事・主な悩み
        - {request.topic}に対する現状の利用状況や意識
        - 性格・価値観

        出力は、各ペルソナを明確に区切って箇条書き形式で記述し、先頭は「ペルソナN: [ペルソナ名]」で始めてください。
        """
        
        personas_text = generate_text(persona_prompt)
        personas = parse_personas(personas_text)
        
        current_session["personas"] = personas
        current_session["start_time"] = time.time()
        
        return {
            "personas": [{"id": i, "name": p.name, "details": p.details} for i, p in enumerate(personas)],
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
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        for persona in selected_personas:
            initial_prompt = f"""
            あなたは以下のペルソナになりきり、インタビュアーの質問に答えてください。
            あなたの回答は、ペルソナの性格、価値観、ライフスタイルに沿った、具体的で血の通った内容にしてください。
            ---
            {persona.raw_text}
            ---
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
async def get_default_questions():
    """デフォルトの質問リストを取得するエンドポイント"""
    questions = [
        "ご自身の簡単な自己紹介（年齢、居住地、職業、家族構成など）をお願いします。",
        "休日の過ごし方について教えてください。どんな人と、どんなことをすることが多いですか？",
        "最近ハマっていること、楽しみにしていることは何ですか？",
        "外食・レジャー・趣味にどのくらいお金を使いますか？どんな基準で使い先を決めていますか？",
        "カラオケに行きたいなと思うのはどんなときですか？",
        "歌うこと以外に、カラオケでやっていることはありますか？",
        "カラオケで歌うことで、どんな気持ちになりますか？",
        "カラオケがなくなったら困ると思いますか？それはなぜですか？"
    ]
    
    return {"questions": questions}

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
        
        analysis_prompt = f"""
        あなたはトップクラスのマーケティングアナリストです。
        以下の3名のペルソナのインタビュー要約を深く読み解き、詳細なインサイト分析レポートを作成してください。
        
        インタビュー要約:
        {all_summaries}
        
        【レポート形式】
        1. **顧客インサイトの要約**: 各ペルソナの回答から得られた、顧客の心理や行動に関する重要な洞察をまとめます。
        2. **共通点と相違点**: 3名のペルソナ間の回答の共通点と、特に注目すべき相違点を分析します。
        3. **マーケティングの示唆**: この分析結果から、どのようなマーケティング戦略やアプローチが考えられるか、具体的な示唆を記述します。
        4. **推奨アクション**: 具体的に実行すべきマーケティング施策を提案します。
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

@app.get("/api/session-status")
async def get_session_status():
    """現在のセッション状態を取得するエンドポイント"""
    return {
        "has_personas": len(current_session["personas"]) > 0,
        "has_selected_personas": len(current_session["selected_personas"]) > 0,
        "selected_persona_count": len(current_session["selected_personas"]),
        "personas": [{"id": i, "name": p.name} for i, p in enumerate(current_session["personas"])],
        "selected_personas": [{"name": p.name} for p in current_session["selected_personas"]]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
