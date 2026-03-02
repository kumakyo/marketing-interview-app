#!/bin/bash
# マーケティングインタビューアプリ - 簡単起動スクリプト

set -e

echo "🚀 マーケティングインタビューアプリを起動します"
echo "=================================================="

cd /home/silver/marketing-interview-app

# ステップ1: 既存プロセスを停止
echo ""
echo "📝 既存のプロセスを停止中..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true
pkill -f node 2>/dev/null || true
sleep 3
echo "✅ 既存プロセスを停止しました"

# ステップ2: 環境変数を確認・設定
echo ""
echo "📝 環境変数を確認中..."
if ! grep -q "NEXT_PUBLIC_API_URL=http://localhost:8000" .env 2>/dev/null; then
    echo "⚠️  .envファイルを修正中..."
    cat > .env << 'EOF'
# Google Gemini API Key
GOOGLE_API_KEY="AIzaSyBG5sSBZqm14RY2JMob_zPUDqhw4sRNEXg"

# フロントエンド設定（HTTPモード）
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth設定
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-secret-key-here-change-in-production
EOF
    echo "✅ .envをHTTPモードに設定"
else
    echo "✅ .envは正しく設定されています"
fi

# frontend/.env.local も修正（これが優先される）
echo "📝 frontend/.env.local を確認中..."
if [ -f "frontend/.env.local" ]; then
    if ! grep -q "NEXT_PUBLIC_API_URL=http://localhost:8000" frontend/.env.local 2>/dev/null; then
        echo "⚠️  frontend/.env.local を修正中..."
        cat > frontend/.env.local << 'EOF'
# API URL - HTTPモード
NEXT_PUBLIC_API_URL=http://localhost:8000

# Node.js SSL設定
NODE_TLS_REJECT_UNAUTHORIZED=0
EOF
        echo "✅ frontend/.env.local をHTTPモードに設定"
    else
        echo "✅ frontend/.env.local は正しく設定されています"
    fi
fi

# ステップ3: 証明書を削除（HTTPモード）
echo ""
echo "📝 HTTPモードで起動するため証明書を削除..."
rm -rf certs frontend/certificates 2>/dev/null || true
echo "✅ 証明書を削除しました"

# ステップ4: キャッシュをクリア
echo ""
echo "📝 キャッシュをクリア中..."
rm -rf frontend/.next 2>/dev/null || true
rm -rf frontend/node_modules/.cache 2>/dev/null || true
echo "✅ キャッシュをクリアしました"

# ステップ5: サーバーを起動
echo ""
echo "📝 サーバーを起動中..."
python3 start-ultra-simple.py > server.log 2>&1 &
SERVER_PID=$!
echo "   PID: $SERVER_PID"

# ステップ6: 起動を確認
echo ""
echo "📝 サーバーの起動を確認中（30秒待機）..."
sleep 30

# バックエンドの確認
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ バックエンド起動OK (http://localhost:8000)"
else
    echo "❌ バックエンドの起動に失敗しました"
    echo "   ログを確認: tail -100 server.log"
    exit 1
fi

# フロントエンドの確認
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q "200"; then
    echo "✅ フロントエンド起動OK (http://localhost:3001)"
else
    echo "⚠️  フロントエンドの起動確認に失敗（まだ起動中の可能性があります）"
    echo "   15秒後に再確認..."
    sleep 15
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q "200"; then
        echo "✅ フロントエンド起動OK (http://localhost:3001)"
    else
        echo "⚠️  フロントエンドの起動が遅れています"
        echo "   手動で確認してください: http://localhost:3001"
    fi
fi

# 最終メッセージ
echo ""
echo "=================================================="
echo "✅ アプリケーションが起動しました！"
echo ""
echo "🌐 ブラウザでアクセス:"
echo "   http://localhost:3001"
echo ""
echo "📚 API文書:"
echo "   http://localhost:8000/docs"
echo ""
echo "📊 サーバーログ:"
echo "   tail -f server.log"
echo ""
echo "🛑 停止方法:"
echo "   pkill -f uvicorn && pkill -f 'next dev'"
echo ""
echo "=================================================="
echo ""
echo "⚠️  重要: ブラウザで以下を実行してください:"
echo "   1. http://localhost:3001 にアクセス"
echo "   2. Ctrl + Shift + R でハードリフレッシュ"
echo "   3. F12でDevToolsを開いてConsoleを確認"
echo ""
echo "   Console に以下が表示されるはずです:"
echo "   🔗 API Base URL: http://localhost:8000"
echo ""
