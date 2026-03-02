#!/bin/bash
# API接続テストスクリプト

echo "🔍 API接続テストを実行中..."
echo "=================================="

# バックエンドテスト
echo ""
echo "1️⃣ バックエンド (http://localhost:8000)"
BACKEND_RESPONSE=$(curl -s http://localhost:8000)
if [ $? -eq 0 ]; then
    echo "   ✅ 応答: $BACKEND_RESPONSE"
else
    echo "   ❌ 接続失敗"
    exit 1
fi

# フロントエンドテスト
echo ""
echo "2️⃣ フロントエンド (http://localhost:3001)"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ ステータス: $FRONTEND_STATUS"
else
    echo "   ❌ ステータス: $FRONTEND_STATUS"
    exit 1
fi

# プロセス確認
echo ""
echo "3️⃣ プロセス確認"
UVICORN_COUNT=$(ps aux | grep -c "[u]vicorn")
NEXT_COUNT=$(ps aux | grep -c "[n]ext-server")
echo "   Uvicorn: $UVICORN_COUNT プロセス"
echo "   Next.js: $NEXT_COUNT プロセス"

if [ $UVICORN_COUNT -gt 0 ] && [ $NEXT_COUNT -gt 0 ]; then
    echo "   ✅ すべてのプロセスが起動中"
else
    echo "   ❌ プロセスが不足"
    exit 1
fi

# 環境変数確認
echo ""
echo "4️⃣ 環境変数確認"
if grep -q "NEXT_PUBLIC_API_URL=http://localhost:8000" .env; then
    echo "   ✅ NEXT_PUBLIC_API_URL: http://localhost:8000"
else
    echo "   ⚠️  NEXT_PUBLIC_API_URL が正しく設定されていない可能性があります"
fi

# ポート確認
echo ""
echo "5️⃣ ポート確認"
PORT_8000=$(ss -tln | grep -c ":8000")
PORT_3001=$(ss -tln | grep -c ":3001")
echo "   ポート 8000: $([[ $PORT_8000 -gt 0 ]] && echo '✅ リッスン中' || echo '❌ 閉じている')"
echo "   ポート 3001: $([[ $PORT_3001 -gt 0 ]] && echo '✅ リッスン中' || echo '❌ 閉じている')"

echo ""
echo "=================================="
echo "✅ すべてのテストが成功しました！"
echo ""
echo "📱 ブラウザでアクセス:"
echo "   http://localhost:3001"
echo ""
echo "🔍 ブラウザのDevTools（F12）を開いて以下を確認してください:"
echo "   1. Console タブで「API Base URL: http://localhost:8000」が表示される"
echo "   2. エラーが表示されない"
echo "   3. Network タブでリクエストが成功している（緑色の200）"
echo ""
echo "⚠️  もしまだエラーが出る場合:"
echo "   1. ブラウザでハードリフレッシュ（Ctrl + Shift + R）"
echo "   2. ブラウザのキャッシュをクリア"
echo "   3. シークレットモードで開く"










