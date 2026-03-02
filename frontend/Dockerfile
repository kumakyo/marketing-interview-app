# Cloud Run用 フロントエンドDockerfile
# マルチステージビルドで軽量化

# ステージ1: 依存関係のインストールとビルド
FROM node:18-alpine AS builder

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール（開発依存関係も含む）
RUN npm ci

# アプリケーションコードをコピー
COPY . .

# 環境変数をビルド引数として受け取る
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Next.jsアプリケーションをビルド
RUN npm run build

# ステージ2: 本番環境用の軽量イメージ
FROM node:18-alpine AS runner

WORKDIR /app

# 本番環境の設定
ENV NODE_ENV=production
ENV PORT=8080

# 必要なファイルのみをコピー
COPY --from=builder /app/next.config.* ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/package.json ./package.json

# 非rootユーザーで実行
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
RUN chown -R nextjs:nodejs /app
USER nextjs

# ポートを公開（Cloud Runは8080を期待）
EXPOSE 8080

# アプリケーションを実行
CMD ["node", "server.js"]
