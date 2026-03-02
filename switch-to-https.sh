#!/bin/bash
# HTTPSモードに切り替えるスクリプト

echo "🔐 HTTPSモードへの切り替えを開始します..."
echo "=================================="

# 現在のディレクトリを確認
if [ ! -f "start-ultra-simple.py" ]; then
    echo "❌ marketing-interview-appディレクトリで実行してください"
    exit 1
fi

# ステップ1: SSL証明書を生成
echo ""
echo "📝 ステップ1: SSL証明書の生成"
if [ -f "./generate-cert.sh" ]; then
    chmod +x ./generate-cert.sh
    ./generate-cert.sh
    echo "✅ 証明書生成完了"
else
    echo "⚠️  generate-cert.shが見つかりません"
    echo "   以下のコマンドで証明書を生成してください："
    echo "   mkdir -p certs && cd certs"
    echo "   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj '/CN=localhost'"
    exit 1
fi

# ステップ2: .envファイルを更新
echo ""
echo "📝 ステップ2: .envファイルをHTTPSモードに更新"
cat > .env << 'EOF'
# Google Gemini API Key
# https://makersuite.google.com/app/apikey から取得してください
GOOGLE_API_KEY="AIzaSyBG5sSBZqm14RY2JMob_zPUDqhw4sRNEXg"

# フロントエンド設定（HTTPSモード）
NEXT_PUBLIC_API_URL=https://localhost:8000

# NextAuth設定（将来のGoogle認証用）
NEXTAUTH_URL=https://localhost:3001
NEXTAUTH_SECRET=your-secret-key-here-change-in-production
EOF
echo "✅ .envファイル更新完了"

# frontend/.env.local も更新
echo "📝 frontend/.env.local をHTTPSモードに更新"
cat > frontend/.env.local << 'EOF'
# API URL - HTTPSモード
NEXT_PUBLIC_API_URL=https://localhost:8000

# Node.js SSL設定 - 自己署名証明書を許可
NODE_TLS_REJECT_UNAUTHORIZED=0
EOF
echo "✅ frontend/.env.local 更新完了"

# ステップ3: Next.jsキャッシュをクリア
echo ""
echo "📝 ステップ3: Next.jsキャッシュをクリア"
if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    echo "✅ キャッシュをクリアしました"
else
    echo "ℹ️  キャッシュが既にクリアされています"
fi

# ステップ4: サーバーを再起動
echo ""
echo "📝 ステップ4: サーバーの再起動"
echo "   現在のプロセスを停止中..."
pkill -9 -f uvicorn 2>/dev/null
pkill -9 -f "next dev" 2>/dev/null
pkill -9 -f "next-server" 2>/dev/null
pkill -9 -f node 2>/dev/null
pkill -9 -f python3 2>/dev/null
sleep 3

echo "   HTTPSモードでサーバーを起動中..."
python3 start-ultra-simple.py &
STARTUP_PID=$!

# ステップ5: 起動確認
echo ""
echo "📝 ステップ5: 起動確認（30秒待機）"
sleep 30

if ps -p $STARTUP_PID > /dev/null; then
    echo "✅ サーバーが起動しました"
else
    echo "❌ サーバーの起動に失敗しました"
    exit 1
fi

# ステップ6: ユーザーへの指示
echo ""
echo "=================================="
echo "✅ HTTPSモードへの切り替えが完了しました！"
echo ""
echo "🌐 次の手順で証明書を承認してください："
echo ""
echo "1️⃣ ブラウザで以下のURLを開く："
echo "   https://localhost:8000"
echo ""
echo "   ⚠️ 警告が表示されます："
echo "   - Chrome: 「この接続ではプライバシーが保護されません」"
echo "     → 「詳細設定」→「localhost にアクセスする（安全ではありません）」"
echo "   - Firefox: 「警告: 潜在的なセキュリティリスクあり」"
echo "     → 「リスクを受け入れて続行」"
echo "   - Safari: 「この接続はプライベートではありません」"
echo "     → 「詳細を表示」→「Webサイトを閲覧」"
echo ""
echo "2️⃣ ブラウザで以下のURLを開く："
echo "   https://localhost:3001"
echo ""
echo "   同様に証明書の警告を承認してください。"
echo ""
echo "3️⃣ アプリケーションにアクセス："
echo "   https://localhost:3001"
echo ""
echo "   今度はエラーなくアクセスできるはずです！"
echo ""
echo "=================================="
echo ""
echo "💡 ヒント:"
echo "   - 証明書は自己署名なので、警告は正常です"
echo "   - 本番環境では Let's Encrypt などの正式な証明書を使用してください"
echo "   - HTTPに戻したい場合は、.envを編集して http:// に変更し、"
echo "     certs フォルダを削除して再起動してください"
echo ""




