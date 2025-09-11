# マーケティングインタビューシステム 🎤

AIを活用したマーケティングインタビューとインサイト分析システムです。ペルソナを自動生成し、深掘りインタビューを実行してマーケティングインサイトを発見できます。

**🖥️ デスクトップアプリケーション対応！別ウィンドウで起動する使いやすいGUIアプリです。**

## 🚀 機能

- **ペルソナ自動生成**: 任意のトピックに基づいて多様なペルソナを自動生成
- **インタラクティブなペルソナ選択**: 生成されたペルソナから3名を選択
- **深掘りインタビュー**: メイン質問と更問を組み合わせた詳細インタビュー
- **インサイト分析**: AIによる総合的なマーケティング分析とレポート生成
- **美しいUI/UX**: Next.js + Tailwind CSSによるモダンなインターフェース
- **🖥️ デスクトップアプリ**: Electronによる別ウィンドウでの直感的な操作

## 🏗️ アーキテクチャ

```
marketing-interview-app/
├── backend/          # FastAPI バックエンド
│   ├── main.py      # APIサーバー
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # Next.js フロントエンド
│   ├── src/
│   │   ├── app/     # App Router
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 📋 前提条件

- Docker & Docker Compose
- Google Generative AI API キー（Gemini API）

## 🛠️ セットアップ

### 🖥️ デスクトップアプリとして起動（推奨）

#### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd marketing-interview-app
```

#### 2. 環境変数の設定

```bash
# .envファイルを作成
cp env.example .env

# .envファイルを編集してGoogle API キーを設定
nano .env
```

#### 3. アプリケーションを起動

**方法1: 新しい確実なランチャー（推奨）**
```bash
python3 start-desktop.py
```

**方法2: オリジナルランチャー**
```bash
python3 launch-app-simple.py
```

**方法3: シェルスクリプト**
```bash
chmod +x launch-app.sh
./launch-app.sh
```

#### 4. 使用開始
- 別ウィンドウでアプリケーションが開きます
- 初回起動時は依存関係が自動的にインストールされます
- デスクトップアプリとして直感的に操作できます

### 🌐 Webアプリとして起動（Docker）

```bash
# 環境変数設定
cp env.example .env
# .envファイルでGOOGLE_API_KEYを設定

# Docker Composeで起動
docker-compose up --build
```

**アクセス先:**
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 🚀 ローカル開発

### バックエンド

```bash
cd backend
pip install -r requirements.txt
export GOOGLE_API_KEY=your_api_key
uvicorn main:app --reload
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

## 📖 使用方法

### 1. トピック入力
インタビューしたい話題（例：「カラオケの新しい利用方法」）を入力します。

### 2. ペルソナ生成
AIが自動的に多様な価値観とライフスタイルを持つ5人のペルソナを生成します。

### 3. ペルソナ選択
生成されたペルソナから3名を選択します。各ペルソナの詳細情報を確認できます。

### 4. インタビュー実行
デフォルトの質問または編集した質問を使用してインタビューを実行します。各質問に対して自動的に更問も生成されます。

### 5. インサイト分析
すべてのインタビュー結果を基に、AIが総合的なマーケティングインサイト分析を生成します。

## 🔧 API エンドポイント

### ペルソナ関連
- `POST /api/generate-personas` - ペルソナ生成
- `POST /api/select-personas` - ペルソナ選択

### インタビュー関連
- `GET /api/default-questions` - デフォルト質問取得
- `POST /api/conduct-interview` - インタビュー実行

### 分析関連
- `POST /api/generate-analysis` - インサイト分析生成

### セッション関連
- `GET /api/session-status` - セッション状態取得

## 🎨 UI/UX 特徴

- **レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応
- **プログレス表示**: 5ステップのワークフローを視覚化
- **リアルタイムフィードバック**: ローディング状態とエラーハンドリング
- **インタラクティブカード**: ペルソナ選択やインタビュー結果の表示
- **アクセシビリティ**: キーボードナビゲーションとスクリーンリーダー対応

## 📊 技術スタック

### バックエンド
- **FastAPI**: 高性能Pythonフレームワーク
- **Google Generative AI**: Gemini APIを使用したテキスト生成
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGIサーバー

### フロントエンド
- **Next.js 14**: React フレームワーク（App Router）
- **TypeScript**: 型安全性
- **Tailwind CSS**: ユーティリティファーストCSS
- **Axios**: HTTP クライアント
- **Electron**: デスクトップアプリケーション化

### インフラ
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナオーケストレーション

## 🔐 セキュリティ

- 環境変数によるAPIキー管理
- CORS設定によるクロスオリジン制御
- 入力バリデーション
- エラーハンドリング

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

1. Forkプロジェクト
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Requestを作成

## 🐛 バグレポート・機能要求

GitHubのIssuesページからバグレポートや機能要求をお送りください。

## 📞 サポート

質問やサポートが必要な場合は、GitHubのDiscussionsページをご利用ください。

---

**注意**: このアプリケーションはGoogle Generative AI APIを使用するため、APIの利用料金が発生する可能性があります。使用前に料金体系をご確認ください。


## 🔧 トラブルシューティング

### 1. システム環境チェック

まず、システム環境をチェックしてください：

```bash
python3 check-system.py
```

### 2. Electronエラーの修正

`libatk-1.0.so.0: cannot open shared object file` エラーが発生した場合：

```bash
# Electron依存ライブラリをインストール
chmod +x install-electron-deps.sh
./install-electron-deps.sh
```

### 3. 依存関係エラーの修正

`ERESOLVE unable to resolve dependency tree` エラーが発生した場合：

```bash
# 依存関係を修正
python3 fix-dependencies.py

# または手動で修正
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### 4. 動作テスト

アプリケーションの動作をテスト：

```bash
python3 test-app.py
```

### 5. 接続問題のデバッグ

「読み込んでいます」から進まない場合：

```bash
python3 debug-connection.py
```

### 6. ビルドエラーの修正

「Build Error」や「Failed to compile」が発生した場合：

```bash
python3 fix-build-errors.py
```

## 🚀 起動手順

### 初回セットアップ
```bash
cd /home/kyosuke/marketing-interview-app
cp env.example .env
# .envファイルでGOOGLE_API_KEYを設定
```

### アプリケーション起動

#### 方法1: Webアプリとして起動（推奨）
```bash
python3 start-web.py
```
- ブラウザで自動的に開きます
- Electronの問題を回避できます
- 最も安定した動作

#### 方法2: デスクトップアプリとして起動
```bash
python3 start-desktop.py
```
- 別ウィンドウで起動
- Electronライブラリが必要

#### 方法3: Docker使用
```bash
docker-compose up --build
```