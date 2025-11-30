#!/bin/bash
# SSL証明書生成スクリプト（開発環境用）

echo "🔐 開発環境用のSSL証明書を生成しています..."

# 証明書保存ディレクトリを作成
mkdir -p certs

# 自己署名証明書を生成
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=Development/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:10.146.0.2"

if [ $? -eq 0 ]; then
    echo "✅ SSL証明書の生成が完了しました"
    echo "📁 証明書の場所: $(pwd)/certs/"
    echo ""
    echo "⚠️  注意: これは開発環境用の自己署名証明書です"
    echo "    ブラウザで「この接続ではプライバシーが保護されません」という警告が表示されますが、"
    echo "    「詳細設定」→「localhost にアクセスする（安全ではありません）」をクリックして進んでください"
else
    echo "❌ SSL証明書の生成に失敗しました"
    exit 1
fi

