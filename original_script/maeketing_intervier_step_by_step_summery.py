# -*- coding: utf-8 -*-
"""インタビュー_改善_都度出力.ipynb

# セットアップ
"""

import google.generativeai as genai
import textwrap
import re
import time
import os

# --- APIキーの設定 ---
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("環境変数 'GOOGLE_API_KEY' が設定されていません。")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"エラー: {e}")
    exit()

# --- 料金計算のための定数 ---
INPUT_TOKEN_PRICE = 0.0000007 / 1000
OUTPUT_TOKEN_PRICE = 0.0000021 / 1000

# --- グローバル変数 ---
total_input_chars = 0
total_output_chars = 0
start_time = time.time()
output_file = None
all_personas_full_history = {}
all_personas_chat_sessions = {}
all_personas_summaries = {}

def print_and_log(text, end='\n'):
    """コンソールとログファイルの両方に書き込む関数"""
    print(text, end=end)
    if output_file:
        output_file.write(text + end)

def to_text(text):
    """テキストを整形するヘルパー関数"""
    text = text.replace('•', ' *')
    return textwrap.dedent(text)

def generate_text(prompt, model_name="models/gemini-1.5-flash", temperature=0.8):
    """指定されたプロンプトと設定でテキストを生成する関数"""
    global total_input_chars, total_output_chars
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature))
        
        total_input_chars += len(prompt)
        if response.text:
            total_output_chars += len(response.text)
        
        return response.text
    except Exception as e:
        print_and_log(f"テキスト生成中にエラーが発生しました: {e}")
        return "エラー：テキストを生成できませんでした。"

def get_conversation_log(history):
    """チャット履歴から対話ログを整形して返す関数。"""
    log = ""
    for message in history:
        role = "インタビュアー" if message.role == "user" else "🗣️"
        # partsがリストの場合があるので、textプロパティを持つ要素だけを処理
        text_parts = [part.text for part in message.parts if hasattr(part, 'text')]
        if text_parts:
            log += f"{role}: {text_parts[0]}\n"
    return log

def parse_questions(question_text):
    """複数行の質問テキストを個別の質問リストに分割する関数"""
    # 修正: 正規表現を、#の数に関わらず行頭から抽出するように変更
    questions_and_titles = re.findall(r'^[#]+\s*(.+)', question_text, re.MULTILINE)
    return [q.strip() for q in questions_and_titles if q.strip()]


def conduct_interview_flow(persona_name, chat_session, questions, topic, is_hypothesis_phase=False, previous_summary=""):
    """
    一問一答形式でインタビューを進め、各回答ごとに3回の更問を行う関数。
    出力は都度コンソールに表示されます。
    """
    global all_personas_full_history
    
    interview_phase_title = '仮説検証' if is_hypothesis_phase else '初回'
    print_and_log(f"\n\n--- {persona_name}へのインタビューログ（{interview_phase_title}） ---")

    if not questions:
        print_and_log("⚠️ 質問リストが空のため、インタビューをスキップします。")
        return

    for i, question in enumerate(questions):
        # メイン質問
        print_and_log(f"\nQ{i+1}: {question}")
        response = chat_session.send_message(f"次の質問に回答してください：{question}")
        answer = response.text
        print_and_log(f"🗣️ {persona_name}の回答: {answer}")
        
        # 更問を3回繰り返す
        for follow_up_num in range(1, 4):
            # プロンプトに要約を含める
            current_conversation_log = get_conversation_log(chat_session.history[-2:])
            
            # 更問プロンプトの調整
            follow_up_prompt = f"""
            あなたは優秀なインタビュアーです。これまでの{persona_name}さんとの会話履歴を読んで、
            特に直前の回答について、具体的な行動や感情、潜在的なニーズをさらに深掘りするような、
            1つの簡潔で具体的な質問を作成してください。
            質問は「〇〇について、もう少し詳しく教えていただけますか？」のような対話形式でお願いします。
            
            ---
            これまでのインタビュー要約:
            {previous_summary if previous_summary else 'まだ要約はありません。'}
            ---
            直前の会話履歴:
            {current_conversation_log}
            ---
            """
            
            if is_hypothesis_phase:
                follow_up_prompt = f"""
                あなたは戦略的なインタビュアーです。これまでの{persona_name}さんとの会話履歴を読み、
                提示された仮説を検証するために、直前の回答について、より具体的で洞察的な情報を引き出すような、
                1つの質問を作成してください。
                質問は「〇〇について、どのように感じますか？」のような対話形式でお願いします。
                ---
                これまでのインタビュー要約:
                {previous_summary if previous_summary else 'まだ要約はありません。'}
                ---
                直前の会話履歴:
                {current_conversation_log}
                ---
                """

            follow_up_question = generate_text(follow_up_prompt, temperature=0.7)
            
            # 更問の回答
            if follow_up_question and "エラー" not in follow_up_question:
                print_and_log(f"    - 更問({follow_up_num}): {follow_up_question}")
                try:
                    follow_up_response = chat_session.send_message(follow_up_question)
                    follow_up_answer = follow_up_response.text
                    print_and_log(f"    - 🗣️ {persona_name}の更問回答: {follow_up_answer}")
                except Exception as e:
                    print_and_log(f"    - 更問への回答生成中にエラーが発生しました: {e}")
                    break
            else:
                print_and_log(f"    - 更問({follow_up_num})の生成に失敗しました。次の質問に進みます。")
                break

    all_personas_full_history[persona_name] = list(chat_session.history)
    print_and_log(f"\n--- {persona_name}さんへの{interview_phase_title}インタビューが終了しました。 ---")

# --- メインプログラム開始 ---
def main():
    global output_file, total_input_chars, total_output_chars, start_time, all_personas_full_history, all_personas_chat_sessions, all_personas_summaries
    
    # ログファイルの設定
    log_dir = "output"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_filename = os.path.join(log_dir, f"interview_report_step_by_step_suumery_{timestamp}.txt")
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        print_and_log("LLMマーケティングインタビューシステムへようこそ！")
        
        # --- ペルソナ生成 ---
        print_and_log("\n--- ペルソナ生成 ---")
        topic = input("インタビューしたい話題は何ですか？ (例: カラオケの新しい利用方法): ")
        print_and_log(f"ユーザー入力: {topic}")
        print_and_log(f"選択された話題: {topic}\n")

        print_and_log("ペルソナを5名生成中です...少々お待ちください。\n")
        persona_prompt = f"""
        あなたはマーケティングの専門家です。
        「{topic}」に関するインタビューのための、多様な価値観とライフスタイルを持つ5人のペルソナを作成してください。
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
        - {topic}に対する現状の利用状況や意識
        - 性格・価値観

        出力は、各ペルソナを明確に区切って箇条書き形式で記述し、先頭は「ペルソナN: [ペルソナ名]」で始めてください。
        """
        personas_text = generate_text(persona_prompt)
        print_and_log("---生成されたペルソナ---")
        print_and_log(to_text(personas_text))

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
                name_match = re.search(r'ペルソナ\d+:\s*(.+)', lines[0])
                details['ペルソナ名'] = name_match.group(1).strip() if name_match else f"ペルソナ{i+1}"
            parsed_personas.append(details)

        if len(parsed_personas) < 3:
            print_and_log("ペルソナの生成に失敗しました。再度お試しください。")
            exit()

        # --- ペルソナと質問の選択 ---
        print_and_log("\n---インタビュー対象ペルソナの選択 (3名)---")
        for i, p in enumerate(parsed_personas):
            print_and_log(f"[{i+1}] {p.get('ペルソナ名', f'ペルソナ {i+1}')}")

        selected_indices = []
        while len(selected_indices) < 3:
            try:
                choice_str = input(f"インタビューしたいペルソナの番号を3つ、カンマ区切りで入力してください (例: 1,3,5): ")
                print_and_log(f"ユーザー入力: {choice_str}")
                choices = [int(c.strip()) for c in choice_str.split(',')]
                if len(choices) != 3:
                    print_and_log("エラー: 3つの番号を入力してください。")
                    continue
                if any(c < 1 or c > len(parsed_personas) for c in choices):
                    print_and_log(f"エラー: 1から{len(parsed_personas)}までの番号を入力してください。")
                    continue
                if len(set(choices)) != 3:
                    print_and_log("エラー: 重複しない3つの番号を入力してください。")
                    continue
                selected_indices = [c - 1 for c in choices]
            except ValueError:
                print_and_log("エラー: 数値をカンマ区切りで正しく入力してください。")

        selected_personas = [parsed_personas[i] for i in selected_indices]
        print_and_log("\n---選択されたペルソナ---")
        for p in selected_personas:
            print_and_log(f"- {p.get('ペルソナ名')}")

        # --- 質問記入 ---
        interview_questions_text = """
#1. 生活背景・現在のライフスタイル理解
##ご自身の簡単な自己紹介（年齢、居住地、職業、家族構成など）をお願いします。
##休日の過ごし方について教えてください。どんな人と、どんなことをすることが多いですか？
##最近ハマっていること、楽しみにしていることは何ですか？
##外食・レジャー・趣味にどのくらいお金を使いますか？どんな基準で使い先を決めていますか？

#2. カラオケの利用実態
##初めてカラオケに行ったときのことを覚えていますか？どんな体験でしたか？
##最近1年間でカラオケに行った回数、誰と、どんな目的で行ったかを教えてください。
##カラオケに行くときの定番の流れ（入り→注文→過ごし方→出るまで）を具体的に教えてください。
##よく利用するカラオケブランドとその理由は？
##カラオケの持ち込みやデリバリー利用についての考えは？

#3. カラオケの楽しみ方・心理的価値
##カラオケに行きたいなと思うのはどんなときですか？
##歌うこと以外に、カラオケでやっていることはありますか？（例：推し活、動画鑑賞、トーク、ゲームなど）
##点数機能などの採点を使いますか？使う場合、どんな楽しみ方やルールを設けていますか？
##カラオケ中にゲーム感覚で遊ぶルールや罰ゲームをした経験はありますか？
##一緒に行くメンバーによって楽しみ方は変わりますか？（年代差、会社の人、推し仲間など）

#4. 歌唱・承認欲求・自己表現
##カラオケで歌うことで、どんな気持ちになりますか？（例：すっきりする、承認される、盛り上がる）
##歌が上手な人は“得している”と思いますか？それはどんな場面で？
##「歌がうまくなりたい」と思ったことはありますか？それはなぜですか？
##SNSで歌をシェアしたり、他人の歌を観たりすることはありますか？
##小さい頃に歌を教えてくれる人がいたら、今と違っていたと思いますか？

#5. カラオケに対する位置づけと比較
##カラオケと、家、カフェ、ファミレス、ホテル、レンタルスペースなどを比較して、どのような特徴がありますか？
##カラオケが「家代わり」「秘密基地」「部室」「実家より自由」と感じたことはありますか？
##一人でカラオケに行くことはありますか？そのときの目的や気分は？
##カラオケがなくなったら困ると思いますか？それはなぜですか？

#6. ブランド評価・機能評価
##よく利用するカラオケブランドごとの印象（設備、清潔感、対応、料金、機能など）はどう違いますか？
##「まねきねこ」「ビッグエコー」「ジャンカラ」「パセラ」などについて、印象の違いや使い分けは？
##「まねきねこ＝白くて明るい」「ビッグエコー＝最新」「ジャンカラ＝安い」などの印象はありますか？
##店員対応や機器の使いやすさ、Bluetooth・HDMIの接続サポートは気になりますか？
##推し活用途としてのカラオケ（鑑賞、装飾、誕生会など）で、理想の空間とは？

#7. カラオケにあったらいいと思う新機能／改善点
##歌声保存・本人音源機能・デュエット録音などがあれば使いたいと思いますか？
##コメントやスタンプなどリアルタイムで送る機能があればどう使いますか？
##カラオケの部屋のデザインや設備で理想的なものはどんなものですか？（例：ソファ、プロジェクター、Wi-Fi等）

#8. ライフステージ・生活環境による影響
##実家暮らし／一人暮らしでカラオケの使い方に変化はありましたか？
##仕事をするようになってからのカラオケに対する意識の変化は？
##結婚・育児などライフステージが変わってもカラオケを使うと思いますか？

#9. カラオケの新しいコンセプトについて
##インタビュー参加者に、以下のような異なる方向性の3つのカラオケコンセプトをビジュアル付きまたは言葉で提示します

###コンセプトA. 自然体で気楽に歌って、笑って、気持ちスッキリ！「カラオケ まねきねこ」
####ストレス発散に、カラオケで熱唱して大盛り上がりもたまにはいいけど
####日常のもやもやを発散するのに、気合を入れすぎるのはちょっと大げさ。
####「まねきねこ」は、気軽に訪れて、肩の力を抜きながら“歌うこと”を楽しめる場所。心がほっこりする親身な接客に、綺麗で明るく居心地がいい部屋、カラオケなのに、まるで家のように“心安らぐ”特別な空間。
####自宅で鼻歌を歌うように、のびのびと歌って、笑って。終わってみれば気持ちスッキリ！自然体のまま、気楽に、気軽に気持ちを発散できる、あなたに一番身近なカラオケ「まねきねこ」

###コンセプトB. 自然と盛り上がれるから、仲が深まる。心の距離がグッと縮まる「カラオケ まねきねこ」
####カラオケって、みんなで盛り上がるとやっぱり楽しい。
####でも、場を盛り上げるためにちょっと気をつかうこと、ありませんか？
####「カラオケ まねきねこ」なら、仲間と”自然と盛り上がれる！”そんな工夫がいっぱい詰まっています。
####例えば──アーティスト本人の声で一緒に歌ってくれる、まねきねこだけの新機能があるから、最新曲でも気負わず楽しめて、みんなで自然と盛り上がれます！さらに、食べ物から、遊び道具、部屋の飾りつけまで何でも持ち込み自由だから、「何持ってく？」と買い出しからワクワク時間が始まっています。
####みんながやりたいことだから、盛り上げなくても、盛り上がる
####仲の良い友達とも、ちょっと気をつかう人とも、もっと仲良くなりたいあの人とも、
####“自然と盛り上がれる”から、心の距離がグッと縮まります

###コンセプトC. 歌うだけじゃない、しゃべって、食べて、遊んで。自由に楽しめるプライベート空間「まねきねこ」
####実はいま、カラオケ「まねきねこ」が “歌う場所”を超えて、いろんな楽しみ方ができる、自由な遊びの拠点になってるって知ってましたか？
####「まねきねこ」は自分たちのペースで、自由に過ごせるプライベート空間。
####飲み物も！食べ物も！ゲームも飾り付けも！何でも自由に持ち込めるから、やりたいことを楽しめます。 いつものように友達とワイワイ歌ったり、まったりおしゃべりしたり、
####お菓子パーティをしながらゲーム大会、大画面で動画を観たり、推し活まで。
####使い方が自由だから、思いっきり楽しめる。
####そしてスタッフも、あなたの「これやってみたい！」に寄り添い、自由に気持ちよく楽しめるよう、そっとサポートしてくれます。
####“歌うだけじゃないカラオケ”の楽しみ方、見つけてみませんか？
####「まねきねこ」は、あなたの“やりたい”が叶う、一番自由で身近な遊び場です。
        """
        
        initial_questions = parse_questions(interview_questions_text)
        print_and_log("\n---初回インタビューで使用する質問を準備しました---")

        # 【全フェーズの共通設定】
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # 各ペルソナに対して、一連のインタビュープロセスを実行
        for persona in selected_personas:
            persona_name = persona.get('ペルソナ名')
            print_and_log(f"\n{'='*20}\n🎤 {persona_name}さんへのインタビューを開始します。\n{'='*20}")

            initial_persona_setting_prompt = f"""
            あなたは以下のペルソナになりきり、インタビュアーの質問に答えてください。
            あなたの回答は、ペルソナの性格、価値観、ライフスタイルに沿った、具体的で血の通った内容にしてください。
            ---
            {persona.get('raw_text')}
            ---
            それでは、インタビューを始めます。準備ができたら「はい、準備ができました」と答えてください。
            """
            chat = model.start_chat(history=[
                {'role': 'user', 'parts': [initial_persona_setting_prompt]},
                {'role': 'model', 'parts': ['はい、準備ができました。何でも聞いてください。']}
            ])
            all_personas_chat_sessions[persona_name] = chat
            all_personas_full_history[persona_name] = list(chat.history)

            # --- フェーズ1: 初回インタビュー（一問一答＋更問3回） ---
            print_and_log("\n--- フェーズ1: 初回インタビューを開始します（一問一答形式） ---")
            conduct_interview_flow(persona_name, chat, initial_questions, topic)
            
            # フェーズ間の要約を自動実行
            current_log = get_conversation_log(all_personas_full_history[persona_name])
            summary_prompt = f"""
            あなたは優秀なアナリストです。以下のペルソナへのインタビュー履歴を読み、
            これまでの会話の重要なポイントを簡潔に、箇条書きで要約してください。
            
            ---
            ペルソナ情報:
            {persona.get('raw_text')}
            ---
            会話履歴:
            {current_log}
            ---
            """
            interview_summary = generate_text(summary_prompt, temperature=0.5)
            
            print_and_log(f"\n--- {persona_name}さんへのインタビュー要約 ---")
            print_and_log(to_text(interview_summary))
            
            all_personas_summaries[persona_name] = interview_summary # 要約を保存

        # --- 【フェーズ1】初回インサイト分析 ---
        print_and_log("\n" + "="*20 + "\n📊 初回インタビューのインサイト分析を実行します。\n" + "="*20)
        
        # 要約を基に分析する
        initial_summary_text = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in all_personas_summaries.items()])
        
        analysis_prompt_1_template = """
        あなたはトップクラスのマーケティングアナリストです。
        以下の3名のペルソナ情報と、彼らへのインタビュー要約を深く読み解き、詳細なインサイト分析レポートを作成してください。
        ---
        ペルソナ情報:
        {persona_info_text}
        ---
        インタビュー要約:
        {interview_summary_text}
        ---
        【レポート形式】
        1. **顧客インサイトの要約**: 各ペルソナの回答から得られた、顧客の心理や行動に関する重要な洞察をまとめます。
        2. **共通点と相違点**: 3名のペルソナ間の回答の共通点と、特に注目すべき相違点を分析します。
        3. **マーケティングの示唆**: この分析結果から、どのようなマーケティング戦略やアプローチが考えられるか、具体的な示唆を記述します。
        4. **未解決の疑問点**: インタビューだけでは明確にならなかった、さらなる調査が必要な点を挙げます。
        """
        analysis_prompt_1 = analysis_prompt_1_template.format(
            persona_info_text='\n---\n'.join([p.get('raw_text') for p in selected_personas]),
            interview_summary_text=initial_summary_text
        )

        initial_analysis_result = generate_text(analysis_prompt_1)
        print_and_log("--- 初回インサイト分析レポート ---")
        print_and_log(to_text(initial_analysis_result))

        # --- 【フェーズ2】仮説構築と追加質問の生成 ---
        print_and_log("\n" + "="*20 + "\n🤔 マーケティング仮説と検証用質問を生成します。\n" + "="*20)
        hypothesis_prompt_template = """
        あなたは戦略プランナーです。
        先ほどのインサイト分析レポートを基に、次のアクションに繋がる「マーケティング仮説」と、その仮説を検証するための「追加インタビュー質問」を作成してください。
        ---
        分析レポート:
        {analysis_report_text}
        ---
        【出力形式】
        **マーケティング仮説**:
        - [仮説1]
        - [仮説2]
        - ...

        **追加インタビュー質問**:
        - [仮説を検証するための質問1]
        - [仮説を検証するための質問2]
        - ...

        ※追加質問は、仮説検証に特化し、具体的で単一の論点に絞った質問を複数作成してください。
        """
        hypothesis_and_new_questions_text = generate_text(hypothesis_prompt_template.format(
            analysis_report_text=initial_analysis_result
        ))
        print_and_log("--- 生成された仮説と追加質問 ---")
        print_and_log(to_text(hypothesis_and_new_questions_text))

        final_hypothesis_and_new_questions_text = hypothesis_and_new_questions_text
        
        # 修正: 質問抽出の正規表現と処理をより頑健に
        new_questions_match = re.search(r'追加インタビュー質問:\s*\n(.+)', hypothesis_and_new_questions_text, re.DOTALL)
        extracted_new_questions = []
        if new_questions_match:
            raw_questions_block = new_questions_match.group(1).strip()
            # 行頭の - または * から始まる行を質問として抽出
            extracted_new_questions = re.findall(r'^[*-]\s*(.+)', raw_questions_block, re.MULTILINE)
            # さらに、Q1: や 1. などの形式にも対応
            if not extracted_new_questions:
                extracted_new_questions = re.findall(r'^(?:Q\d+|#\d+|\d+\.|[*-])\s*(.+)', raw_questions_block, re.MULTILINE)

            extracted_new_questions = [q.strip() for q in extracted_new_questions if q.strip()]

        if not extracted_new_questions:
            print_and_log("仮説検証のための追加質問の抽出に失敗しました。デフォルト質問を使用します。")
            extracted_new_questions = ["これまでの仮説について、他に何か深掘りしたい点はありますか？"]

        # --- 【フェーズ2】再インタビューの実施 ---
        print_and_log("\n" + "="*20 + "\n🎯 仮説検証のための追加インタビューを実施します。\n" + "="*20)

        for persona in selected_personas:
            persona_name = persona.get('ペルソナ名')
            print_and_log(f"\n{'*'*10} {persona_name}さんへの仮説検証インタビューを開始します {'*'*10}")
            
            chat = all_personas_chat_sessions[persona_name]
            
            # 既存の会話ログに追記していく
            conduct_interview_flow(persona_name, chat, extracted_new_questions, topic, 
                                 is_hypothesis_phase=True, previous_summary=all_personas_summaries.get(persona_name, ""))

        # --- 【フェーズ3】最終インサイト分析 ---
        print_and_log("\n" + "="*20 + "\n📈 最終インサイト分析と戦略提言を実行します。\n" + "="*20)

        # 最終分析プロンプトでも、全ログではなく要約を統合して使用
        final_summary_text = '\n\n'.join([f"--- {name}さんの要約 ---\n{summary}" for name, summary in all_personas_summaries.items()])
        
        final_analysis_prompt_template = """
        あなたは経験豊富なCMO（最高マーケティング責任者）です。
        以下のすべての情報（ペルソナ、初期分析、仮説、そして全インタビューの結果）を統合し、最終的なマーケティング戦略を策定してください。
        ---
        ペルソナ情報:
        {persona_info_text}
        ---
        初期インサイト分析と仮説:
        {hypothesis_and_questions_text}
        ---
        全インタビュー要約:
        {all_summaries_text}
        ---
        【レポート形式】
        1. **最終的なインサイト**: 初回インタビューと仮説検証インタビューから得られた、最も重要な顧客のインサイトを統合して記述します。
        2. **仮説の検証結果**: 立てたマーケティング仮説が、インタビュー結果によってどのように検証されたか（支持されたか、反証されたか）を具体的に説明します。
        3. **推奨するマーケティング戦略**: 最終インサイトと仮説の検証結果に基づき、具体的なアクションプランを含むマーケティング戦略を提言します。
        4. **事業への影響**: この戦略を実行した場合に、事業にもたらされるであろうポジティブな影響について考察します。
        """
        final_analysis_prompt = final_analysis_prompt_template.format(
            persona_info_text='\n---\n'.join([p.get('raw_text') for p in selected_personas]),
            hypothesis_and_questions_text=final_hypothesis_and_new_questions_text,
            all_summaries_text=final_summary_text
        )

        final_analysis_result = generate_text(final_analysis_prompt)
        print_and_log("--- 最終分析レポート：マーケティング戦略提言 ---")
        print_and_log(to_text(final_analysis_result))

        print_and_log("\nすべてのプロセスが完了しました。システムのご利用ありがとうございました！")

        # --- 最終的なレポートとコスト表示 ---
        end_time = time.time()
        elapsed_time = end_time - start_time

        estimated_cost = (total_input_chars * INPUT_TOKEN_PRICE) + (total_output_chars * OUTPUT_TOKEN_PRICE)

        print_and_log("\n\n" + "="*50)
        print_and_log("⭐ プログラム実行サマリー ⭐")
        print_and_log(f"総実行時間: {elapsed_time:.2f} 秒")
        print_and_log(f"API入力文字数（概算）: {total_input_chars} 文字")
        print_and_log(f"API出力文字数（概算）: {total_output_chars} 文字")
        print_and_log(f"推定API利用料金: 約 ${estimated_cost:.6f}")
        print_and_log("==================================================")

if __name__ == "__main__":
    main()