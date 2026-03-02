#!/bin/bash
# 🌐 外部IPアドレス対応の設定スクリプト

set -e  # エラーで停止

# 色付き出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 外部IPアドレス
EXTERNAL_IP="136.110.120.131"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}🌐 外部IP対応の設定を適用${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# プロジェクトルートの確認
if [ ! -f "start-ultra-simple.py" ]; then
    echo -e "${RED}❌ エラー: marketing-interview-appディレクトリで実行してください${NC}"
    exit 1
fi

# ========================================
# ステップ1: バックエンドのCORS設定を更新
# ========================================
echo -e "${YELLOW}📝 [1/4] バックエンドのCORS設定を更新${NC}"

# backend/main.pyのCORS設定に外部IPを追加
if grep -q "http://${EXTERNAL_IP}:3001" backend/main.py; then
    echo -e "${GREEN}✅ CORSに外部IPが既に設定されています${NC}"
else
    # CORSの origins リストに外部IPを追加
    sed -i "/allow_origins=\[/,/\]/s|\]|    \"http://${EXTERNAL_IP}:3001\",\n    \"https://${EXTERNAL_IP}:3001\",\n]|" backend/main.py
    echo -e "${GREEN}✅ CORSに外部IPを追加しました${NC}"
fi

# ========================================
# ステップ2: 環境変数を更新（オプション）
# ========================================
echo ""
echo -e "${YELLOW}📝 [2/4] 環境変数の確認${NC}"

# .envに外部IP情報を追加（コメントとして）
if ! grep -q "EXTERNAL_IP" .env; then
    echo "" >> .env
    echo "# 外部IPアドレス情報" >> .env
    echo "# EXTERNAL_IP=${EXTERNAL_IP}" >> .env
    echo "# 外部からのアクセス: https://${EXTERNAL_IP}:3001" >> .env
    echo -e "${GREEN}✅ .envに外部IP情報を追加しました${NC}"
else
    echo -e "${GREEN}✅ .envに外部IP情報が既に存在します${NC}"
fi

# ========================================
# ステップ3: GCPファイアウォールの確認
# ========================================
echo ""
echo -e "${YELLOW}📝 [3/4] GCPファイアウォールの確認${NC}"
echo ""
echo -e "${BLUE}以下のポートがGCPファイアウォールで開放されているか確認してください：${NC}"
echo ""
echo -e "   ${YELLOW}● ポート 8000${NC} (バックエンドAPI)"
echo -e "   ${YELLOW}● ポート 3001${NC} (フロントエンド)"
echo ""
echo -e "${BLUE}GCP Console で確認する手順：${NC}"
echo -e "   1. ${BLUE}https://console.cloud.google.com/${NC} にアクセス"
echo -e "   2. 「VPC ネットワーク」→「ファイアウォール」"
echo -e "   3. 新しいルールを作成（必要に応じて）："
echo -e "      - ${YELLOW}名前:${NC} allow-marketing-interview"
echo -e "      - ${YELLOW}ターゲット:${NC} すべてのインスタンス（または特定のタグ）"
echo -e "      - ${YELLOW}ソースIPの範囲:${NC} 0.0.0.0/0"
echo -e "      - ${YELLOW}プロトコルとポート:${NC} tcp:8000,3001"
echo ""
read -p "ファイアウォール設定を確認しましたか？ (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  ファイアウォール設定を確認してから再実行してください${NC}"
    exit 1
fi

echo -e "${GREEN}✅ ファイアウォール確認完了${NC}"

# ========================================
# ステップ4: サーバーの再起動準備
# ========================================
echo ""
echo -e "${YELLOW}📝 [4/4] サーバーの再起動準備${NC}"

# 既存のプロセスを確認
if pgrep -f "uvicorn" > /dev/null 2>&1 || pgrep -f "next dev" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  既存のサーバープロセスが実行中です${NC}"
    echo -e "${YELLOW}   サーバーを再起動しますか？ (y/n)${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}サーバーを停止中...${NC}"
        ./stop-servers.sh
        echo -e "${GREEN}✅ サーバーを停止しました${NC}"
    fi
else
    echo -e "${GREEN}✅ サーバープロセスは実行されていません${NC}"
fi

# ========================================
# 完了メッセージ
# ========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 外部IP対応の設定が完了しました！${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🚀 次のステップ:${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. サーバーを起動:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   ${BLUE}python3 start-ultra-simple.py${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. ブラウザで証明書を承認（3つのURL）:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   ${BLUE}A. バックエンド（ローカル）:${NC}"
echo -e "      https://localhost:8000"
echo ""
echo -e "   ${BLUE}B. フロントエンド（ローカル）:${NC}"
echo -e "      https://localhost:3001"
echo ""
echo -e "   ${BLUE}C. バックエンド（外部IP）:${NC}"
echo -e "      ${YELLOW}https://${EXTERNAL_IP}:8000${NC}"
echo ""
echo -e "   ${BLUE}D. フロントエンド（外部IP）:${NC}"
echo -e "      ${YELLOW}https://${EXTERNAL_IP}:3001${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. 外部からアクセス:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   ${YELLOW}https://${EXTERNAL_IP}:3001${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 証明書承認の方法:${NC}"
echo ""
echo -e "   ${YELLOW}● Chrome/Edge:${NC}"
echo -e "      - 警告画面で「${BLUE}thisisunsafe${NC}」と入力"
echo -e "      - または「詳細設定」→「アクセスする」"
echo ""
echo -e "   ${YELLOW}● Firefox:${NC}"
echo -e "      - 「詳細設定」→「例外を追加」→「承認」"
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🌐 準備完了！外部IPからアクセスできます！${NC}"
echo ""

