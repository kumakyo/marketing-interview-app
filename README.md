# tames interview

AIを活用したマーケティングインタビューシステム

## 🎯 概要

tames interviewは、Google Gemini AIを使用してマーケティングインタビューを自動化し、深いインサイトを得るためのツールです。

### 主な機能

- 🤖 **AIペルソナ生成**: 商品・サービス情報から多様なインタビュー対象者を自動生成
- 💬 **対話型インタビュー**: AIペルソナとの自然な対話形式でのインタビュー実施
- 📊 **多角的分析**: 市場構造、消費者ニーズ、商品改善の3つの視点から分析
- 🔐 **Google認証**: 安全なログインとユーザー別データ管理
- 📝 **履歴管理**: 過去のインタビュー結果の保存と閲覧
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

3. SSL証明書の生成（HTTPS使用時）
```bash
./generate-cert.sh
```

4. 依存パッケージのインストールと起動
```bash
python3 start-ultra-simple.py
```

アプリケーションが起動したら、ブラウザで以下にアクセス：
- フロントエンド: `https://localhost:3001`
- API文書: `https://localhost:8000/docs`

## 📖 詳細ドキュメント

- [HTTPS設定ガイド](HTTPS_SETUP.md)
- [Google認証実装ガイド](AUTH_IMPLEMENTATION_GUIDE.md)

## 🛠️ 技術スタック

### フロントエンド
- Next.js 15.5
- React 18
- TypeScript
- Tailwind CSS
- NextAuth.js

### バックエンド
- Python 3.12
- FastAPI
- Google Generative AI (Gemini)
- Uvicorn
- SQLite (予定)

## 📋 使い方

### 1. プロジェクト設定
- 商品・サービス情報を入力
- 競合情報を入力（任意）
- 分析目的を選択（市場構造、消費者ニーズ、商品改善）
- インタビュー対象者の人数を設定

### 2. ペルソナ選択
- AIが生成した多様なペルソナから選択
- 各ペルソナの詳細情報を確認

### 3. インタビュー実行
- 質問内容を編集・追加可能
- Excelファイルから質問をインポート可能

### 4. 結果分析
- 選択した分析タイプに基づいた詳細レポート
- ペルソナ別のインタビュー詳細
- 追加質問機能

## 🔑 環境変数

以下の環境変数を`.env`ファイルに設定してください：

```bash
# 必須: Google Gemini API Key
GOOGLE_API_KEY="your_gemini_api_key_here"

# オプション: Google OAuth 2.0 (認証機能使用時)
GOOGLE_CLIENT_ID="your_google_client_id_here"
GOOGLE_CLIENT_SECRET="your_google_client_secret_here"
NEXTAUTH_SECRET="your_nextauth_secret_here"
NEXTAUTH_URL="https://localhost:3001"
```

### APIキーの取得方法

1. **Google Gemini API Key**
   - [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
   - APIキーを作成

2. **Google OAuth 2.0** (認証機能使用時)
   - [Google Cloud Console](https://console.cloud.google.com/) にアクセス
   - OAuth 2.0クライアントIDを作成

## 🔐 セキュリティ

- HTTPS通信をサポート
- Google OAuth 2.0認証
- ユーザー別データ分離
- 環境変数による機密情報管理

**⚠️ 重要**: `.env`ファイルや`certs/`ディレクトリをGitにコミットしないでください。

## 📁 プロジェクト構造

```
marketing-interview-app/
├── backend/              # FastAPIバックエンド
│   ├── main.py          # メインアプリケーション
│   └── requirements.txt # Python依存パッケージ
├── frontend/            # Next.jsフロントエンド
│   ├── src/
│   │   ├── app/        # Appルーター
│   │   ├── components/ # Reactコンポーネント
│   │   └── lib/        # ユーティリティ
│   └── package.json    # Node.js依存パッケージ
├── certs/              # SSL証明書（gitignore）
├── venv/               # Python仮想環境（gitignore）
├── .env                # 環境変数（gitignore）
├── .env.example        # 環境変数サンプル
└── start-ultra-simple.py # 起動スクリプト
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

## 📞 サポート

問題が発生した場合は、[Issues](https://github.com/yourusername/marketing-interview-app/issues)で報告してください。

---

© 2025 tames interview. All rights reserved.
