#!/bin/bash
# セットアップスクリプト

echo "🚀 マーケティングインタビューシステムのセットアップを開始します..."
echo "=================================================="

# .envファイルが存在しない場合はenv.exampleからコピー
if [ ! -f .env ]; then
    echo "📝 .envファイルを作成中..."
    cp env.example .env
    echo "✅ .envファイルを作成しました"
    echo "⚠️  .envファイルを開いて、Gemini APIキーを設定してください"
else
    echo "✅ .envファイルは既に存在します"
fi

# Pythonバックエンドの依存関係をインストール
echo ""
echo "🐍 Pythonバックエンドの依存関係をインストール中..."

# pipまたはpip3を探す
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif python3 -m pip --version &> /dev/null; then
    PIP_CMD="python3 -m pip"
else
    echo "⚠️  pipが見つかりません。pipをインストールします..."
    # pipをインストール
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-pip
        PIP_CMD="pip3"
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
        PIP_CMD="pip3"
    else
        echo "❌ pipを自動インストールできません。手動でpipをインストールしてください。"
        echo "   sudo apt-get install python3-pip"
        exit 1
    fi
fi

echo "   pip コマンド: $PIP_CMD"
cd backend
$PIP_CMD install -r requirements.txt

cd ..
echo "✅ Pythonバックエンドの依存関係をインストールしました"

# Node.jsフロントエンドの依存関係をインストール
echo ""
echo "📦 Node.jsフロントエンドの依存関係をインストール中..."
cd frontend
if command -v npm &> /dev/null; then
    npm install
    cd ..
    echo "✅ Node.jsフロントエンドの依存関係をインストールしました"
else
    cd ..
    echo "⚠️  npmが見つかりません。"
    echo "   Node.jsをインストールしてください："
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    echo ""
    echo "   または、Node.js公式サイトからダウンロード："
    echo "   https://nodejs.org/"
    echo ""
    echo "✅ バックエンドのセットアップは完了しました"
fi

echo ""
echo "=================================================="
echo "✅ セットアップが完了しました！"
echo ""
echo "📝 次のステップ:"
echo "1. .envファイルを開いてGemini APIキーを設定してください"
echo "   GOOGLE_API_KEY=your_actual_api_key_here"
echo ""
echo "2. アプリケーションを起動してください:"
echo "   python3 start-ultra-simple.py"
echo ""

