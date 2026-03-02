# tames interview

AIを活用したマーケティングインタビューシステム

## 🎯 概要

tames interviewは、Google Gemini AIを使用してマーケティングインタビューを自動化し、深いインサイトを得るためのツールです。

### 主な機能

- 🤖 **AIペルソナ生成**: 商品・サービス情報から多様なインタビュー対象者を自動生成
- 💬 **対話型インタビュー**: AIペルソナとの自然な対話形式でのインタビュー実施
- 🧠 **深層心理解析**: インタビュー中の発言から本音や感情を推測・分析
- 📊 **多角的分析**: 市場構造、消費者ニーズ、商品改善の3つの視点から包括的分析
- 🔐 **Google認証**: 安全なログインとユーザー別データ管理
- 💾 **データ永続化**: すべてのプロジェクト・インタビュー結果をデータベースに保存
- 📝 **履歴管理**: 過去のインタビュー結果の保存と閲覧
- 🔄 **入力履歴**: 過去の入力内容を参照して自動記入
- 👥 **マルチユーザー**: 複数ユーザーが同時利用可能（データ分離）
- 🔒 **HTTPS対応**: セキュアな通信

## 🚀 クイックスタート

### 前提条件

- Python 3.12+
- Node.js 18+
- Google Gemini API Key
- (オプション) Google OAuth 2.0 認証情報

### インストール

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/marketing-interview-app.git
cd marketing-interview-app
```

2. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して、APIキーを設定
```

### 起動方法

**簡単起動（推奨）**
```bash
./start.sh
```

このスクリプトは以下を自動で行います：
- 既存プロセスの停止
- 環境変数の確認・設定（HTTPモード）
- 証明書の削除（HTTPモード用）
- キャッシュのクリア
- サーバーの起動
- 起動確認

**手動起動**
```bash
# 既存プロセスを停止
pkill -f uvicorn && pkill -f "next dev"
sleep 3

# サーバーを起動
python3 start-ultra-simple.py
```

**起動後のアクセス**
- フロントエンド: https://localhost:3001
- バックエンドAPI: https://localhost:8000
- API文書: https://localhost:8000/docs

### ⚠️ **重要：初回アクセス時の設定**

**1. バックエンドの証明書を承認（必須）**

新しいブラウザタブで開く：
```
https://localhost:8000
```

証明書の警告が表示される → 画面上でキーボードで `thisisunsafe` と入力

成功すると以下のJSONが表示される：
```json
{"message":"マーケティングインタビューシステム API"}
```

**2. フロントエンドにアクセス**
```
https://localhost:3001
```

証明書の警告が表示される → 同様に `thisisunsafe` と入力

**3. ブラウザをリフレッシュ**
- `Ctrl + Shift + R`（ハードリフレッシュ）
- これでネットワークエラーが解消される

### HTTPへの切り替え（オプション）

HTTPS証明書の承認が面倒な場合は、HTTPモードに戻すことも可能：

```bash
./start.sh
```

その後、`http://localhost:3001` でアクセス（証明書承認不要）

詳細は [VERIFICATION_AND_HTTPS_GUIDE.md](VERIFICATION_AND_HTTPS_GUIDE.md) を参照。

### 動作確認

サーバーの状態を確認するには：
```bash
./test-connection.sh
```

## 📖 詳細ドキュメント

### セットアップガイド
- [HTTPS完全移行ガイド](HTTPS完全移行ガイド.md) - HTTPS設定の完全ガイド
- [検証・HTTPS対応ガイド](VERIFICATION_AND_HTTPS_GUIDE.md) - 検証とHTTPS対応
- [Google OAuth設定ガイド](GOOGLE_OAUTH_SETUP.md) - Google認証の設定手順

### トラブルシューティング
- [ネットワークエラー解決ガイド](NETWORK_ERROR_FIXED.md) - ネットワークエラーの解決
- [CORS問題のトラブルシューティング](CORS_TROUBLESHOOTING.md) - CORS問題の診断と解決

### 実装ガイド
- [認証実装ガイド](AUTH_IMPLEMENTATION_GUIDE.md) - Google認証の実装詳細
- [認証設定完了ガイド](AUTH_SETUP_COMPLETE.md) - OAuth環境変数設定

## 🛠️ 技術スタック

### フロントエンド
- Next.js 15.5
- React 18
- TypeScript
- Tailwind CSS
- NextAuth.js (Google OAuth 2.0)
- Axios

### バックエンド
- Python 3.12
- FastAPI
- Google Generative AI (Gemini)
- Uvicorn
- SQLAlchemy
- SQLite

## 🏗️ システム構成

```
┌─────────────────────────────────────────────────────┐
│            ユーザー（ブラウザ）                        │
│         Googleアカウント認証                          │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS/HTTP
                     ↓
┌─────────────────────────────────────────────────────┐
│         Next.js Frontend (Port 3001)                │
│  ┌──────────────────────────────────────────────┐   │
│  │ NextAuth.js (Google OAuth)                   │   │
│  │ - ログイン/ログアウト                          │   │
│  │ - セッション管理                               │   │
│  │ - JWTトークン生成                              │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ React Components                             │   │
│  │ - プロジェクト設定フォーム                      │   │
│  │ - ペルソナ選択カード                           │   │
│  │ - チャットインタビュー                         │   │
│  │ - 深層心理解析表示                             │   │
│  │ - 包括的分析レポート                           │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ API Client (Axios)                           │   │
│  │ - Authorization: Bearer <token>              │   │
│  │ - HTTPS/HTTP対応                              │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ REST API + JWT Token
                     ↓
┌─────────────────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)                 │
│  ┌──────────────────────────────────────────────┐   │
│  │ 認証ミドルウェア                               │   │
│  │ - JWTトークン検証                              │   │
│  │ - ユーザー情報抽出                             │   │
│  │ - 権限チェック                                 │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ API Endpoints                                │   │
│  │ - POST /api/generate-personas                │   │
│  │ - POST /api/conduct-interview                │   │
│  │ - POST /api/analyze-psychology               │   │
│  │ - POST /api/generate-analysis                │   │
│  │ - GET  /api/user/projects                    │   │
│  │ - GET  /api/user/statistics                  │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ AI Integration (Google Gemini)               │   │
│  │ - ペルソナ生成                                 │   │
│  │ - インタビュー実施                             │   │
│  │ - 深層心理解析                                 │   │
│  │ - 包括的分析レポート                           │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │ Database Manager                             │   │
│  │ - プロジェクト保存/取得                         │   │
│  │ - ペルソナ保存/取得                            │   │
│  │ - インタビュー結果保存/取得                     │   │
│  │ - ユーザー統計情報                             │   │
│  └──────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ SQLAlchemy ORM
                     ↓
┌─────────────────────────────────────────────────────┐
│         SQLite Database                             │
│  ┌──────────────────────────────────────────────┐   │
│  │ Tables                                       │   │
│  │ - users (ユーザー情報)                         │   │
│  │   - id, email, name, picture, created_at     │   │
│  │                                               │   │
│  │ - projects (プロジェクト)                      │   │
│  │   - id, user_id, topic, products, ...        │   │
│  │                                               │   │
│  │ - personas (ペルソナ)                          │   │
│  │   - id, project_id, name, details, ...       │   │
│  │                                               │   │
│  │ - interviews (インタビュー)                     │   │
│  │   - id, persona_id, messages, psychology     │   │
│  │                                               │   │
│  │ - analyses (分析結果)                          │   │
│  │   - id, project_id, content, type, ...       │   │
│  │                                               │   │
│  │ - interview_sessions (セッション)              │   │
│  │   - session_id, user_id, state, ...          │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### データフロー

1. **認証フロー**
   ```
   ユーザー → Googleログイン → NextAuth.js → JWTトークン発行
   → フロントエンド（セッション保持） → API呼び出し時にトークン送信
   → バックエンド（トークン検証） → ユーザー識別
   ```

2. **インタビューフロー**
   ```
   プロジェクト設定 → ペルソナ生成（Gemini） → ペルソナ選択
   → インタビュー実施（Gemini） → 深層心理解析（Gemini）
   → 包括的分析（Gemini） → データベース保存 → 結果表示
   ```

3. **データ永続化フロー**
   ```
   各ステップの完了時 → db_manager → SQLAlchemy → SQLite
   → ユーザー別に分離保存 → 履歴閲覧可能
   ```

### マルチユーザー対応

- **セッション管理**: NextAuth.jsによるGoogle OAuth認証
- **データ分離**: ユーザーIDによるデータベース分離
- **同時実行**: 各ユーザーが独立してシステムを利用可能
- **履歴保存**: ユーザーごとの過去のプロジェクト・インタビュー履歴

### セキュリティ

- **認証**: Google OAuth 2.0
- **通信**: HTTPS/HTTP対応
- **認可**: Bearer Token (JWT)
- **データ分離**: ユーザーIDによるアクセス制御
- **環境変数**: 機密情報の安全な管理

## 📋 使い方

### 0. ログイン
- Googleアカウントでログイン
- ログイン後、ユーザー情報が表示される

### 1. プロジェクト設定
- 商品・サービス情報を入力（過去の入力が自動記入される）
- 競合情報を入力（任意）
- トピック（目的）を入力
- 分析タイプを選択（市場構造、消費者ニーズ、商品改善から複数選択可）
- インタビュー対象者の人数を設定（1〜10人）

### 2. ペルソナ生成と選択
- AIが自動でペルソナを生成
- 生成されたペルソナから好きなものを選択
- 各ペルソナの詳細情報（年齢、性別、職業、趣味など）を確認

### 3. インタビュー実行
- AIペルソナとチャット形式でインタビュー
- ペルソナの回答から**深層心理を解析**
  - 本音（真の考え）
  - 感情（感じている気持ち）
  - 購買影響（購買意欲への影響）
  - 示唆（マーケティング上の示唆）
- リアルタイムで深層心理が表示される

### 4. 結果分析と保存
- 選択した分析タイプに基づいた**包括的レポート**
- ペルソナ別のインタビュー詳細
- **エビデンス付きサマリ**（発言と深層心理を統合）
- すべての結果はデータベースに自動保存

### 5. 履歴閲覧
- 過去のプロジェクト一覧を閲覧
- ユーザー統計情報（プロジェクト数、インタビュー数）
- 他のユーザーのデータは見れない（データ分離）

## 🔑 環境変数

以下の環境変数を`.env`ファイルに設定してください：

```bash
# 必須: Google Gemini API Key
GOOGLE_API_KEY="your_gemini_api_key_here"

# 必須: API URL (フロントエンドが使用)
NEXT_PUBLIC_API_URL="https://localhost:8000"

# 必須: Google OAuth 2.0
GOOGLE_CLIENT_ID="your_google_client_id_here"
GOOGLE_CLIENT_SECRET="your_google_client_secret_here"

# 必須: NextAuth設定
NEXTAUTH_SECRET="your_nextauth_secret_here"
NEXTAUTH_URL="https://localhost:3001"

# オプション: Node.js SSL設定（開発環境）
NODE_TLS_REJECT_UNAUTHORIZED="0"
```

### 🔐 APIキーの取得方法

#### 1. Google Gemini API Key（必須）
   - [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
   - 「Create API Key」をクリック
   - 生成されたキーを `.env` にコピー

#### 2. Google OAuth 2.0（必須）
   - [Google Cloud Console](https://console.cloud.google.com/) にアクセス
   - プロジェクトを作成（または既存のプロジェクトを選択）
   - 「APIとサービス」→「認証情報」→「認証情報を作成」
   - 「OAuth クライアント ID」を選択
   - アプリケーションの種類: 「ウェブ アプリケーション」
   - 承認済みのリダイレクト URI:
     - `https://localhost:3001/api/auth/callback/google`
     - `http://localhost:3001/api/auth/callback/google`
   - クライアントIDとシークレットを `.env` にコピー

#### 3. NEXTAUTH_SECRET（必須）
   ランダムな文字列を生成：
   ```bash
   openssl rand -base64 32
   ```
   生成された文字列を `.env` にコピー

### 📝 環境変数設定の自動化

OAuth環境変数を自動設定するスクリプト：
```bash
./setup-oauth-env.sh
```
このスクリプトは：
- クライアントIDとシークレットの入力を求める
- NEXTAUTH_SECRETを自動生成
- `.env` と `frontend/.env.local` を自動更新

## 🔐 セキュリティ

### 実装済みセキュリティ機能

- ✅ **HTTPS通信**: 自己署名証明書による暗号化通信（開発環境）
- ✅ **Google OAuth 2.0認証**: 安全なユーザー認証
- ✅ **Bearer Token (JWT)**: API認証とセッション管理
- ✅ **ユーザー別データ分離**: データベースレベルでのアクセス制御
- ✅ **環境変数管理**: 機密情報の安全な管理
- ✅ **CORS設定**: 適切なオリジン制限
- ✅ **SQLite データベース**: ローカルファイルベースの安全な保存

### セキュリティベストプラクティス

1. **機密情報の管理**
   - `.env` ファイルを Git にコミットしない
   - API キーやシークレットを公開しない
   - `certs/` ディレクトリを Git にコミットしない

2. **証明書の管理**
   - 開発環境では自己署名証明書を使用
   - 本番環境では正式なSSL証明書（Let's Encrypt等）を使用
   - 証明書の定期的な更新

3. **データベースの保護**
   - データベースファイルのバックアップ
   - ユーザーごとのアクセス制限
   - 機密情報の暗号化（必要に応じて）

**⚠️ 重要**: 以下のファイルは Git にコミットしないでください：
- `.env`
- `frontend/.env.local`
- `certs/`
- `backend/marketing_interview.db`
- `venv/`
- `frontend/.next/`
- `frontend/node_modules/`

## 📁 プロジェクト構造

```
marketing-interview-app/
├── backend/                    # FastAPIバックエンド
│   ├── main.py                 # メインアプリケーション（API エンドポイント）
│   ├── database.py             # SQLAlchemy モデル定義
│   ├── db_manager.py           # データベース操作ヘルパー
│   ├── auth.py                 # 認証ヘルパー（JWT検証）
│   ├── requirements.txt        # Python依存パッケージ
│   └── marketing_interview.db  # SQLiteデータベース（gitignore）
├── frontend/                   # Next.jsフロントエンド
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                      # メインページ
│   │   │   ├── layout.tsx                    # ルートレイアウト
│   │   │   ├── providers.tsx                 # SessionProvider
│   │   │   ├── auth/
│   │   │   │   └── signin/
│   │   │   │       └── page.tsx              # ログインページ
│   │   │   └── api/
│   │   │       └── auth/
│   │   │           └── [...nextauth]/
│   │   │               └── route.ts          # NextAuth APIルート
│   │   ├── components/                       # Reactコンポーネント
│   │   │   ├── ChatPersonaCard.tsx           # ペルソナカード
│   │   │   ├── ChatInterview.tsx             # インタビューチャット
│   │   │   ├── PsychologyAnalysis.tsx        # 深層心理表示
│   │   │   ├── ComprehensiveAnalysisView.tsx # 分析レポート
│   │   │   └── ...
│   │   ├── lib/                              # ユーティリティ
│   │   │   └── api.ts                        # APIクライアント（Axios）
│   │   └── types/
│   │       └── next-auth.d.ts                # NextAuth型定義
│   ├── package.json                          # Node.js依存パッケージ
│   └── .env.local                            # フロントエンド環境変数（gitignore）
├── certs/                      # SSL証明書（gitignore）
│   ├── cert.pem                # 自己署名証明書
│   └── key.pem                 # 秘密鍵
├── venv/                       # Python仮想環境（gitignore）
├── .env                        # 環境変数（gitignore）
├── .env.example                # 環境変数サンプル
├── start-ultra-simple.py       # 統合起動スクリプト
├── start.sh                    # HTTP起動スクリプト
├── switch-to-https.sh          # HTTPS切り替えスクリプト
├── generate-cert.sh            # 証明書生成スクリプト
├── stop-servers.sh             # サーバー停止スクリプト
└── README.md                   # このファイル
```

## 🤝 コントリビューション

コントリビューションを歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 👥 作成者

- あなたの名前 - [@yourusername](https://github.com/yourusername)

## 🙏 謝辞

- Google Gemini AI
- Next.js
- FastAPI
- すべてのコントリビューター

## 🔧 トラブルシューティング

### ❌ ネットワークエラー: `net::ERR_CERT_AUTHORITY_INVALID`

**原因**: バックエンドの証明書を承認していない

**解決策**:
1. 新しいタブで `https://localhost:8000` を開く
2. 警告画面で `thisisunsafe` とキーボード入力
3. `https://localhost:3001` に戻って `Ctrl + Shift + R`

### ❌ CORS エラー

**原因**: オリジン設定の問題

**解決策**:
```bash
# サーバーを再起動
./stop-servers.sh
python3 start-ultra-simple.py
```

詳細は [CORS_TROUBLESHOOTING.md](CORS_TROUBLESHOOTING.md) 参照

### ❌ ポートが使用中

**原因**: 既存のプロセスが動作中

**解決策**:
```bash
# プロセスを停止
./stop-servers.sh

# または手動で停止
sudo lsof -ti:8000 | xargs -r sudo kill -9
sudo lsof -ti:3001 | xargs -r sudo kill -9
```

### ❌ Google OAuth エラー

**原因**: 環境変数の設定ミス

**解決策**:
1. `.env` ファイルを確認
2. `GOOGLE_CLIENT_ID` と `GOOGLE_CLIENT_SECRET` が正しいか確認
3. `NEXTAUTH_SECRET` が設定されているか確認
4. リダイレクトURIが Google Cloud Console と一致しているか確認

### ❌ データベースエラー

**原因**: データベースファイルの破損

**解決策**:
```bash
# データベースを削除して再作成
rm backend/marketing_interview.db
# サーバーを再起動（自動的に再作成される）
python3 start-ultra-simple.py
```

### 💡 その他のヒント

- **ブラウザのキャッシュをクリア**: `Ctrl + Shift + Delete`
- **開発者ツールでエラーを確認**: `F12` → Console タブ
- **ログを確認**: ターミナルのバックエンド/フロントエンドログを見る

## 📞 サポート

問題が発生した場合は、[Issues](https://github.com/yourusername/marketing-interview-app/issues)で報告してください。

---

© 2025 tames interview. All rights reserved.
