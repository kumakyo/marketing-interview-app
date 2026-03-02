#!/bin/bash
# 🛑 サーバーを安全に停止するスクリプト
# SSH接続を維持しながらアプリケーションサーバーのみを停止

# 色付き出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${YELLOW}🛑 サーバーを停止します${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# バックエンド（uvicorn）の停止
echo -e "${YELLOW}📝 [1/3] バックエンド（uvicorn）を停止${NC}"
if pgrep -f "uvicorn backend.main:app" > /dev/null 2>&1; then
    # より具体的なパターンで停止
    pkill -f "uvicorn backend.main:app" 2>/dev/null || true
    sleep 2
    
    # まだ残っているか確認
    if pgrep -f "uvicorn backend.main:app" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  プロセスがまだ残っています。強制停止します...${NC}"
        pkill -9 -f "uvicorn backend.main:app" 2>/dev/null || true
        sleep 1
    fi
    
    echo -e "${GREEN}✅ バックエンドを停止しました${NC}"
else
    echo -e "${GREEN}✅ バックエンドは実行されていません${NC}"
fi

# フロントエンド（Next.js）の停止
echo ""
echo -e "${YELLOW}📝 [2/3] フロントエンド（Next.js）を停止${NC}"
if pgrep -f "next dev" > /dev/null 2>&1; then
    pkill -f "next dev" 2>/dev/null || true
    sleep 2
    
    # まだ残っているか確認
    if pgrep -f "next dev" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  プロセスがまだ残っています。強制停止します...${NC}"
        pkill -9 -f "next dev" 2>/dev/null || true
        sleep 1
    fi
    
    echo -e "${GREEN}✅ フロントエンドを停止しました${NC}"
else
    echo -e "${GREEN}✅ フロントエンドは実行されていません${NC}"
fi

# start-ultra-simple.pyの停止
echo ""
echo -e "${YELLOW}📝 [3/3] start-ultra-simple.pyを停止${NC}"
if pgrep -f "start-ultra-simple.py" > /dev/null 2>&1; then
    pkill -f "start-ultra-simple.py" 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ start-ultra-simple.pyを停止しました${NC}"
else
    echo -e "${GREEN}✅ start-ultra-simple.pyは実行されていません${NC}"
fi

# 最終確認
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${YELLOW}📝 最終確認${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

if pgrep -f "uvicorn" > /dev/null 2>&1 || pgrep -f "next dev" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  まだ一部のプロセスが残っています：${NC}"
    echo ""
    ps aux | grep -E "(uvicorn|next dev)" | grep -v grep || true
    echo ""
    echo -e "${YELLOW}手動で停止する場合：${NC}"
    echo -e "${BLUE}  pkill -9 -f uvicorn${NC}"
    echo -e "${BLUE}  pkill -9 -f 'next dev'${NC}"
else
    echo -e "${GREEN}✅ すべてのサーバープロセスが停止しました${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}🛑 停止処理完了${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

