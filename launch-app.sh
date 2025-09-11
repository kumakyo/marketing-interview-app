#!/bin/bash

# マーケティングインタビューシステム デスクトップアプリ起動スクリプト

APP_DIR="/home/kyosuke/marketing-interview-app"
FRONTEND_DIR="$APP_DIR/frontend"
BACKEND_DIR="$APP_DIR/backend"

echo "🚀 マーケティングインタビューシステム デスクトップアプリを起動中..."

# ディレクトリ確認
if [ ! -d "$APP_DIR" ]; then
    echo "❌ アプリケーションディレクトリが見つかりません: $APP_DIR"
    exit 1
fi

# .envファイルの確認
if [ ! -f "$APP_DIR/.env" ]; then
    echo "❌ .envファイルが見つかりません。"
    echo "📝 以下のコマンドで.envファイルを作成してください："
    echo "cp $APP_DIR/env.example $APP_DIR/.env"
    echo "その後、.envファイルでGOOGLE_API_KEYを設定してください。"
    exit 1
fi

# Python依存関係の確認とインストール
echo "📦 Python依存関係を確認中..."
cd "$BACKEND_DIR"

# 仮想環境の作成（存在しない場合）
if [ ! -d "venv" ]; then
    echo "🐍 Python仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
source venv/bin/activate

# 依存関係をインストール
pip install -q -r requirements.txt

# Node.js依存関係の確認とインストール
echo "📦 Node.js依存関係を確認中..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "📦 Node.js依存関係をインストール中..."
    npm install
fi

# Electronアプリケーションを開発モードで起動
echo "🖥️  デスクトップアプリケーションを起動中..."
echo "📱 アプリケーションウィンドウが別途開きます..."

# 開発モードでElectronアプリを起動
npm run electron-dev &

# プロセスIDを保存
ELECTRON_PID=$!

echo ""
echo "✅ マーケティングインタビューシステムが起動しました！"
echo ""
echo "💡 使用方法:"
echo "   1. 別ウィンドウでアプリケーションが開きます"
echo "   2. APIキーが設定されていない場合は、$APP_DIR/.envファイルを編集してください"
echo "   3. アプリを終了するには、このターミナルでCtrl+Cを押してください"
echo ""
echo "🛑 停止するには: Ctrl+C"

# Ctrl+Cでの終了処理
trap 'echo "🛑 アプリケーションを終了しています..."; kill $ELECTRON_PID 2>/dev/null; exit 0' INT

# Electronプロセスの終了を待機
wait $ELECTRON_PID
