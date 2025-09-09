FROM node:18-alpine

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci --only=production

# アプリケーションコードをコピー
COPY . .

# Next.jsアプリケーションをビルド
RUN npm run build

# ポートを公開
EXPOSE 3000

# アプリケーションを実行
CMD ["npm", "start"]
