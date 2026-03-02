#!/bin/bash
# 🔒 HTTPS Quick Start - ワンコマンドでHTTPSモードに移行
# 使用方法: ./https-quick-start.sh

set -e  # エラーで停止

# 色付き出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# プロジェクトルートの確認
if [ ! -f "start-ultra-simple.py" ]; then
    echo -e "${RED}❌ エラー: marketing-interview-appディレクトリで実行してください${NC}"
    exit 1
fi

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}🔒 HTTPS Quick Start${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# ========================================
# ステップ1: SSL証明書の生成
# ========================================
echo -e "${YELLOW}📝 [1/6] SSL証明書の生成${NC}"

if [ -f "certs/cert.pem" ] && [ -f "certs/key.pem" ]; then
    echo -e "${GREEN}✅ 証明書が既に存在します（スキップ）${NC}"
else
    mkdir -p certs
    cd certs
    
    echo "   証明書を生成中..."
    openssl req -x509 -newkey rsa:4096 -nodes \
      -keyout key.pem \
      -out cert.pem \
      -days 365 \
      -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Dev/CN=localhost" \
      -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1,IP:0.0.0.0" \
      2>/dev/null
    
    chmod 600 key.pem
    chmod 644 cert.pem
    cd ..
    
    echo -e "${GREEN}✅ SSL証明書を生成しました${NC}"
fi

# ========================================
# ステップ2: 環境変数の更新
# ========================================
echo ""
echo -e "${YELLOW}📝 [2/6] 環境変数をHTTPSモードに更新${NC}"

# プロジェクトルートの .env を更新
sed -i 's|NEXT_PUBLIC_API_URL=http://localhost:8000|NEXT_PUBLIC_API_URL=https://localhost:8000|g' .env
sed -i 's|NEXTAUTH_URL=http://localhost:3001|NEXTAUTH_URL=https://localhost:3001|g' .env

# frontend/.env.local を更新（存在しない場合は作成）
if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << 'EOF'
# API URL - HTTPSモード
NEXT_PUBLIC_API_URL=https://localhost:8000

# Node.js SSL設定 - 自己署名証明書を許可
NODE_TLS_REJECT_UNAUTHORIZED=0
EOF
    echo -e "${GREEN}✅ frontend/.env.local を作成しました${NC}"
else
    sed -i 's|NEXT_PUBLIC_API_URL=http://localhost:8000|NEXT_PUBLIC_API_URL=https://localhost:8000|g' frontend/.env.local
    echo -e "${GREEN}✅ frontend/.env.local を更新しました${NC}"
fi

echo -e "${GREEN}✅ .env ファイル更新完了${NC}"

# ========================================
# ステップ3: 設定の確認
# ========================================
echo ""
echo -e "${YELLOW}📝 [3/6] 設定の確認${NC}"
echo -e "   ${BLUE}プロジェクトルート/.env:${NC}"
grep NEXT_PUBLIC_API_URL .env | sed 's/^/   /'
echo -e "   ${BLUE}frontend/.env.local:${NC}"
grep NEXT_PUBLIC_API_URL frontend/.env.local | sed 's/^/   /'

if grep -q "https://localhost:8000" .env && grep -q "https://localhost:8000" frontend/.env.local; then
    echo -e "${GREEN}✅ 両方のファイルがHTTPSモードに設定されています${NC}"
else
    echo -e "${RED}❌ エラー: 環境変数の設定が正しくありません${NC}"
    exit 1
fi

# ========================================
# ステップ4: 既存プロセスの停止
# ========================================
echo ""
echo -e "${YELLOW}📝 [4/6] 既存プロセスの停止${NC}"

pkill -9 -f uvicorn 2>/dev/null || true
pkill -9 -f "next dev" 2>/dev/null || true
pkill -9 -f node 2>/dev/null || true
pkill -9 -f python3 2>/dev/null || true

sleep 3
echo -e "${GREEN}✅ すべてのプロセスを停止しました${NC}"

# ========================================
# ステップ5: Next.jsキャッシュのクリア
# ========================================
echo ""
echo -e "${YELLOW}📝 [5/6] Next.jsキャッシュのクリア${NC}"

if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    echo -e "${GREEN}✅ キャッシュをクリアしました${NC}"
else
    echo -e "${GREEN}✅ キャッシュは既にクリアされています${NC}"
fi

# ========================================
# ステップ6: サーバーの起動
# ========================================
echo ""
echo -e "${YELLOW}📝 [6/6] HTTPSモードでサーバーを起動${NC}"
echo ""

python3 start-ultra-simple.py &
STARTUP_PID=$!

echo -e "${BLUE}⏳ サーバーの起動を待機中（30秒）...${NC}"
sleep 30

# 起動確認
if ps -p $STARTUP_PID > /dev/null; then
    echo -e "${GREEN}✅ サーバーが正常に起動しました！${NC}"
else
    echo -e "${RED}❌ サーバーの起動に失敗しました${NC}"
    echo -e "${YELLOW}   ログを確認してください: cat ~/.cursor/projects/home-silver/terminals/2.txt${NC}"
    exit 1
fi

# ========================================
# 完了メッセージ
# ========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ HTTPSモードへの移行が完了しました！${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🌐 次の手順で証明書を承認してください：${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ステップ1: バックエンドの証明書を承認${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   1. ブラウザで開く: ${BLUE}https://localhost:8000${NC}"
echo ""
echo -e "   2. ${RED}⚠️  警告画面が表示されます${NC} → ${GREEN}これは正常です！${NC}"
echo ""
echo -e "   3. 証明書を承認:"
echo ""
echo -e "      ${YELLOW}● Google Chrome / Edge:${NC}"
echo -e "         - 「${BLUE}詳細設定${NC}」をクリック"
echo -e "         - 「${BLUE}localhost にアクセスする（安全ではありません）${NC}」をクリック"
echo -e "         ${GREEN}または${NC}"
echo -e "         - 警告画面で「${BLUE}thisisunsafe${NC}」と入力（画面に何も表示されません）"
echo ""
echo -e "      ${YELLOW}● Firefox:${NC}"
echo -e "         - 「${BLUE}詳細設定${NC}」→「${BLUE}例外を追加${NC}」→「${BLUE}セキュリティ例外を承認${NC}」"
echo ""
echo -e "   4. ${GREEN}成功すると以下が表示される:${NC}"
echo -e "      ${BLUE}{\"message\":\"マーケティングインタビューシステム API\"}${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ステップ2: フロントエンドの証明書を承認${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   1. ブラウザで開く: ${BLUE}https://localhost:3001${NC}"
echo ""
echo -e "   2. ${RED}⚠️  再度警告画面が表示されます${NC}"
echo ""
echo -e "   3. ${GREEN}ステップ1と同じ方法で証明書を承認${NC}"
echo ""
echo -e "   4. ${GREEN}成功すると${NC} → ${BLUE}アプリケーションのUIが表示される${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ステップ3: 動作確認${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   1. ${BLUE}F12キー${NC}を押してDevToolsを開く"
echo ""
echo -e "   2. ${YELLOW}Consoleタブ${NC}で確認:"
echo -e "      ${GREEN}✅ 🔗 API Base URL: https://localhost:8000${NC}"
echo -e "      ${GREEN}✅ 🔒 Protocol: https:${NC}"
echo -e "      ${GREEN}✅ CORSエラーが表示されない${NC}"
echo ""
echo -e "   3. ${YELLOW}Networkタブ${NC}で確認:"
echo -e "      ${GREEN}✅ https://localhost:8000/ → 200 OK（緑色）${NC}"
echo -e "      ${GREEN}✅ https://localhost:8000/api/interview-history → 200 OK${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}💡 便利なコマンド:${NC}"
echo ""
echo -e "   ${BLUE}# サーバーの状態を確認${NC}"
echo -e "   ./test-connection.sh"
echo ""
echo -e "   ${BLUE}# ログをリアルタイムで確認${NC}"
echo -e "   tail -f ~/.cursor/projects/home-silver/terminals/2.txt"
echo ""
echo -e "   ${BLUE}# HTTPモードに戻す${NC}"
echo -e "   ./start.sh"
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🔒 安全で快適な開発環境をお楽しみください！${NC}"
echo ""





