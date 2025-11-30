# HTTPS設定について

このアプリケーションはHTTPS（SSL/TLS）に対応しています。

## 開発環境でのHTTPS使用方法

### 1. SSL証明書の生成

プロジェクトルートで以下のコマンドを実行：

```bash
./generate-cert.sh
```

これにより、`certs/`ディレクトリに自己署名証明書が生成されます。

### 2. アプリケーションの起動

```bash
python3 start-ultra-simple.py
```

SSL証明書が存在する場合、自動的にHTTPSモードで起動します。

### 3. ブラウザでのアクセス

- フロントエンド: `https://localhost:3001`
- バックエンドAPI: `https://localhost:8000/docs`

**⚠️ 重要な注意事項:**

自己署名証明書を使用しているため、ブラウザで以下のような警告が表示されます：

- Chrome/Edge: 「この接続ではプライバシーが保護されません」
- Firefox: 「警告: 潜在的なセキュリティリスクあり」

これは正常な動作です。以下の手順で進んでください：

1. **Chrome/Edge の場合:**
   - 「詳細設定」または「Advanced」をクリック
   - 「localhost にアクセスする（安全ではありません）」または "Proceed to localhost (unsafe)" をクリック

2. **Firefox の場合:**
   - 「詳細設定」または「Advanced」をクリック
   - 「危険性を承知で続行」または "Accept the Risk and Continue" をクリック

## HTTPとHTTPSの切り替え

### HTTPSを無効にしてHTTPを使用する場合

`certs/`ディレクトリを削除するか、リネームしてください：

```bash
mv certs certs.backup
```

再度HTTPSを有効にする場合は、元に戻すか証明書を再生成してください：

```bash
mv certs.backup certs
# または
./generate-cert.sh
```

## 本番環境でのHTTPS

本番環境では、**自己署名証明書は使用しないでください**。代わりに：

1. **Let's Encrypt** を使用（無料）
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com
   ```

2. 生成された証明書のパスを使用：
   - 証明書: `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
   - 秘密鍵: `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

3. `certs/`ディレクトリにシンボリックリンクを作成：
   ```bash
   ln -s /etc/letsencrypt/live/yourdomain.com/fullchain.pem certs/cert.pem
   ln -s /etc/letsencrypt/live/yourdomain.com/privkey.pem certs/key.pem
   ```

## トラブルシューティング

### 証明書エラーが発生する場合

証明書を再生成してください：

```bash
rm -rf certs
./generate-cert.sh
```

### フロントエンドからバックエンドへの接続エラー

`frontend/.env.local`ファイルを確認し、以下が設定されていることを確認：

```
NEXT_PUBLIC_API_URL=https://localhost:8000
NODE_TLS_REJECT_UNAUTHORIZED=0
```

### ポート8000または3001が既に使用されている

既存のプロセスを終了してください：

```bash
pkill -f "uvicorn"
pkill -f "next dev"
```

## セキュリティに関する注意

- **開発環境でのみ** `NODE_TLS_REJECT_UNAUTHORIZED=0` を使用してください
- 本番環境では必ず正式な証明書を使用してください
- 自己署名証明書は外部に公開しないでください

