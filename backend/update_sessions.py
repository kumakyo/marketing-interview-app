#!/usr/bin/env python3
"""
バックエンドのcurrent_sessionをセッション対応に一括更新するスクリプト
"""

import re

# main.pyを読み込む
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.content()

# 更新が必要なエンドポイントのパターン
endpoints_to_update = [
    '/api/set-analysis-types',
    '/api/select-personas',
    '/api/default-questions',
    '/api/conduct-interview',
    '/api/generate-analysis',
    '/api/generate-hypothesis',
    '/api/conduct-hypothesis-interview',
    '/api/generate-custom-final-analysis',
    '/api/generate-final-analysis',
    '/api/session-status',
]

# 各エンドポイント定義に session_id パラメータを追加
for endpoint in endpoints_to_update:
    # @app.post("/api/xxx") または @app.get("/api/xxx") のパターンを見つける
    pattern = rf'(@app\.(post|get)\("{re.escape(endpoint)}"\)\s+async def \w+\([^)]*)\)'
    
    def add_session_id(match):
        params = match.group(1)
        # 既に session_id がある場合はスキップ
        if 'session_id' in params:
            return match.group(0)
        # パラメータがある場合は , を追加
        if params.strip().endswith('('):
            return params + 'session_id: str = "default")'
        else:
            return params + ', session_id: str = "default")'
    
    content = re.sub(pattern, add_session_id, content)

# current_session["xxx"] を session["xxx"] に置換（ただし、関数定義内のみ）
# これは複雑なので、手動で主要な箇所のみ置換

# 結果を出力（確認用）
print("更新が必要な箇所を特定しました:")
print(f"- エンドポイント数: {len(endpoints_to_update)}")
print(f"- current_session の使用箇所: {content.count('current_session[')}")

# バックアップを作成してから更新
import shutil
shutil.copy('main.py', 'main.py.backup')
print("バックアップを作成しました: main.py.backup")

# 実際の更新は手動で行うため、ここでは出力のみ
with open('session_update_plan.txt', 'w', encoding='utf-8') as f:
    f.write("セッション対応更新計画\n\n")
    f.write(f"更新が必要なエンドポイント:\n")
    for ep in endpoints_to_update:
        f.write(f"  - {ep}\n")
    f.write(f"\ncurrent_sessionの使用箇所: {content.count('current_session[')}箇所\n")

print("更新計画を session_update_plan.txt に保存しました")

