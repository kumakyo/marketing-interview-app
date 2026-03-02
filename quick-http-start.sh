#!/bin/bash

# HTTPモードで起動するスクリプト

echo "🔄 HTTPモードに切り替えます..."

# サーバーを停止
pkill -9 -f uvicorn
pkill -9 -f "next dev"
pkill -9 -f "start-ultra-simple"
sleep 3

# 証明書を削除
rm -rf certs/
rm -rf frontend/certificates/

# 環境変数をHTTPに設定
sed -i 's|NEXT_PUBLIC_API_URL=https://localhost:8000|NEXT_PUBLIC_API_URL=http://localhost:8000|g' .env
sed -i 's|NEXT_PUBLIC_API_URL=https://localhost:8000|NEXT_PUBLIC_API_URL=http://localhost:8000|g' frontend/.env.local 2>/dev/null || true
sed -i 's|NEXTAUTH_URL=https://localhost:3001|NEXTAUTH_URL=http://localhost:3001|g' .env
sed -i 's|NEXTAUTH_URL=https://localhost:3001|NEXTAUTH_URL=http://localhost:3001|g' frontend/.env.local 2>/dev/null || true

# キャッシュをクリア
rm -rf frontend/.next/

echo "✅ HTTPモードに切り替えました"
echo ""
echo "📍 以下のコマンドでサーバーを起動してください："
echo "   python3 start-ultra-simple.py"
echo ""
echo "📍 その後、以下のURLにアクセス："
echo "   http://localhost:3001"

