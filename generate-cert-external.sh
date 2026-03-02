#!/bin/bash
# 🌐 外部IPアドレス対応のSSL証明書生成スクリプト

# 色付き出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 外部IPアドレス
EXTERNAL_IP="136.110.120.131"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}🌐 外部IP対応SSL証明書を生成${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# プロジェクトルートの確認
if [ ! -f "start-ultra-simple.py" ]; then
    echo -e "${RED}❌ エラー: marketing-interview-appディレクトリで実行してください${NC}"
    exit 1
fi

# 既存の証明書をバックアップ
if [ -d "certs" ]; then
    echo -e "${YELLOW}📦 既存の証明書をバックアップ中...${NC}"
    mv certs "certs.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✅ バックアップ完了${NC}"
fi

# certsディレクトリを作成
mkdir -p certs
cd certs

echo ""
echo -e "${YELLOW}📝 証明書情報:${NC}"
echo -e "   ${BLUE}● localhost${NC}"
echo -e "   ${BLUE}● 127.0.0.1${NC}"
echo -e "   ${BLUE}● 0.0.0.0${NC}"
echo -e "   ${BLUE}● ${EXTERNAL_IP} (外部IP)${NC}"
echo ""

# SSL証明書を生成（外部IPを含む）
echo -e "${YELLOW}🔐 SSL証明書を生成中...${NC}"
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Dev/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1,IP:0.0.0.0,IP:${EXTERNAL_IP}" \
  2>/dev/null

if [ $? -eq 0 ]; then
    chmod 600 key.pem
    chmod 644 cert.pem
    cd ..
    
    echo -e "${GREEN}✅ SSL証明書を生成しました${NC}"
    echo ""
    
    # 証明書の内容を確認
    echo -e "${YELLOW}📋 証明書の詳細:${NC}"
    openssl x509 -in certs/cert.pem -text -noout | grep -A 1 "Subject Alternative Name" || echo "   SANフィールドが見つかりません"
    
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ 外部IP対応の証明書生成完了！${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}📝 次のステップ:${NC}"
    echo -e "   ${BLUE}1.${NC} ./configure-external-ip.sh を実行"
    echo -e "   ${BLUE}2.${NC} サーバーを再起動"
    echo -e "   ${BLUE}3.${NC} https://${EXTERNAL_IP}:3001 にアクセス"
    echo ""
else
    echo -e "${RED}❌ 証明書の生成に失敗しました${NC}"
    exit 1
fi

