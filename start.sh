#!/bin/bash

# マーケティングインタビューシステム 起動スクリプト

echo "🚀 マーケティングインタビューシステムを起動中..."

# .envファイルの存在確認
if [ ! -f .env ]; then
    echo "❌ .envファイルが見つかりません。"
    echo "📝 .envファイルを作成し、GOOGLE_API_KEYを設定してください："
    echo "GOOGLE_API_KEY=your_google_api_key_here"
    exit 1
fi

# Dockerの起動確認
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Dockerがインストールされていません。"
    echo "🐳 Dockerをインストールしてから再実行してください。"
    exit 1
fi

# Docker Composeの起動確認
if ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Docker Composeがインストールされていません。"
    echo "🐳 Docker Composeをインストールしてから再実行してください。"
    exit 1
fi

echo "✅ 環境チェック完了"
echo "🏗️  アプリケーションをビルド・起動中..."

# Docker Composeでアプリケーションを起動
docker-compose up --build -d

echo "⏳ サービス起動を待機中..."
sleep 10

# サービスの状態を確認
echo "📊 サービス状態："
docker-compose ps

echo ""
echo "🎉 マーケティングインタビューシステムが起動しました！"
echo ""
echo "📱 フロントエンド: http://localhost:3000"
echo "🔗 バックエンドAPI: http://localhost:8000"
echo "📚 API ドキュメント: http://localhost:8000/docs"
echo ""
echo "🛑 停止するには: docker-compose down"
echo "📋 ログを確認するには: docker-compose logs"
