# Cloud Run用 バックエンドDockerfile
# Python 3.11 slim版（軽量でCloud Runに最適）
FROM python:3.11-slim

# 作業ディレクトリをバックエンドに設定
WORKDIR /app

# バックエンドの依存関係ファイルをコピー
COPY backend/requirements.txt .

# 依存関係をインストール（キャッシュなしで軽量化）
RUN pip install --no-cache-dir -r requirements.txt

# バックエンドのソースコードをコピー
COPY backend/ .

# Cloud Runのポート設定（デフォルト8080）
ENV PORT=8080

# 本番環境の設定
ENV PYTHONUNBUFFERED=1

# アプリを起動（uvicornで直接起動）
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}