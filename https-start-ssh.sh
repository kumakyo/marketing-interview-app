#!/bin/bash
# 🔒 HTTPS Start for SSH/Remote Environments
# SSH接続環境用のHTTPS起動スクリプト

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
echo -e "${GREEN}🔒 HTTPS Mode Setup (SSH/Remote環境用)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# ========================================
# ステップ1: SSL証明書の生成
# ========================================
echo -e "${YELLOW}📝 [1/5] SSL証明書の生成${NC}"

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
echo -e "${YELLOW}📝 [2/5] 環境変数をHTTPSモードに更新${NC}"

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
echo -e "${YELLOW}📝 [3/5] 設定の確認${NC}"
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
# ステップ4: 既存プロセスの確認（停止はしない）
# ========================================
echo ""
echo -e "${YELLOW}📝 [4/5] 既存プロセスの確認${NC}"

# 実行中のプロセスを確認（停止はしない）
if pgrep -f uvicorn > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  uvicorn プロセスが実行中です${NC}"
    echo -e "${YELLOW}   後で手動で停止してください: pkill -f uvicorn${NC}"
else
    echo -e "${GREEN}✅ uvicorn プロセスは実行されていません${NC}"
fi

if pgrep -f "next dev" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Next.js プロセスが実行中です${NC}"
    echo -e "${YELLOW}   後で手動で停止してください: pkill -f 'next dev'${NC}"
else
    echo -e "${GREEN}✅ Next.js プロセスは実行されていません${NC}"
fi

echo -e "${GREEN}✅ プロセス確認完了（自動停止はSSH接続切断を防ぐためスキップ）${NC}"

# ========================================
# ステップ5: Next.jsキャッシュのクリア
# ========================================
echo ""
echo -e "${YELLOW}📝 [5/5] Next.jsキャッシュのクリア${NC}"

if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    echo -e "${GREEN}✅ キャッシュをクリアしました${NC}"
else
    echo -e "${GREEN}✅ キャッシュは既にクリアされています${NC}"
fi

# ========================================
# 完了メッセージ
# ========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ HTTPS設定が完了しました！${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🚀 次のステップ: サーバーを起動${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}以下のコマンドを実行してサーバーを起動してください：${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}python3 start-ultra-simple.py${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}サーバーが起動したら（30秒後）：${NC}"
echo ""
echo -e "   ${BLUE}1. https://localhost:8000${NC} をブラウザで開いて証明書を承認"
echo -e "   ${BLUE}2. https://localhost:3001${NC} をブラウザで開いて証明書を承認"
echo -e "   ${BLUE}3. F12${NC}キーでDevToolsを開き、CORSエラーがないか確認"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 証明書承認の方法:${NC}"
echo ""
echo -e "   ${YELLOW}● Chrome/Edge:${NC}"
echo -e "      - 「詳細設定」→「localhost にアクセスする（安全ではありません）」"
echo -e "      - または警告画面で「${BLUE}thisisunsafe${NC}」と入力"
echo ""
echo -e "   ${YELLOW}● Firefox:${NC}"
echo -e "      - 「詳細設定」→「例外を追加」→「セキュリティ例外を承認」"
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🔒 準備完了！上記のコマンドでサーバーを起動してください！${NC}"
echo ""


