# マーケティングインタビューシステム 🎤

AIを活用したマーケティングインタビューとインサイト分析システムです。ペルソナを自動生成し、深掘りインタビューを実行してマーケティングインサイトを発見できます。

**🖥️ デスクトップアプリケーション対応！別ウィンドウで起動する使いやすいGUIアプリです。**

## 🚀 機能

### 📋 **プロジェクト管理機能**
- **商品・サービス情報入力**: ターゲット、ベネフィット、根拠、価格等の体系的入力
- **複数商品対応**: ユーザー指定数の商品・サービスを同時に分析
- **競合商品情報**: 競合の価格、特徴、説明を入力して比較分析
- **履歴管理**: 過去のインタビュー結果の保存・閲覧機能

### 🤖 **AI分析機能**
- **ペルソナ自動生成**: 商品・サービス情報に基づく多様なペルソナ生成
- **インタラクティブなペルソナ選択**: 生成されたペルソナから3名を選択
- **深掘りインタビュー**: メイン質問と更問を組み合わせた詳細インタビュー
- **商品適合性分析**: ターゲット顧客とペルソナ反応の適合性評価
- **競合比較分析**: 競合商品との差別化ポイント分析
- **ベネフィット受容性**: 提示ベネフィットの訴求力評価
- **価格戦略分析**: 価格設定の妥当性評価

### 📊 **データ連携機能**
- **Excelアップロード**: 質問リストをExcelファイルから読み取り
- **レポートダウンロード**: 分析結果の詳細レポート出力
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

**方法1: 改善版ランチャー（推奨）**
```bash
python3 start-improved.py
```

**方法2: 新しい確実なランチャー**
```bash
python3 start-desktop.py
```

**方法3: オリジナルランチャー**
```bash
python3 launch-app-simple.py
```

**方法4: シェルスクリプト**
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

### 1. プロジェクト情報入力
- **トピック**: インタビューしたい話題を入力
- **商品・サービス情報**: 以下の4項目を必須入力
  - ①どういった人に向けた商品・サービスか
  - ②その人たちにとってどういう良いこと（ベネフィット）があるか
  - ③そのベネフィットはなぜ実現・体現できるか？（根拠）
  - ④価格などの基本情報
- **競合商品情報**: 競合の名前、説明、価格、特徴（任意）
- **複数商品対応**: 必要に応じて複数の商品・サービスを登録可能

### 2. ペルソナ生成
商品・サービス情報と競合情報を考慮して、AIが多様なペルソナを自動生成します。

### 3. ペルソナ選択
生成されたペルソナから3名を選択します。各ペルソナの詳細情報を確認できます。

### 4. インタビュー質問編集
- **AI生成質問**: 商品・サービス情報に特化した質問を自動生成
- **Excelアップロード**: Excelファイル（.xlsx, .xls）から質問を読み取り
- **手動編集**: 質問の追加、編集、削除が可能

### 5. 初回インタビュー実行
選択したペルソナに対して、商品・サービス情報を考慮したインタビューを実行。

### 6. 初回インサイト分析
- 商品・サービスの市場適合性分析
- 競合商品との比較分析
- ターゲット顧客の妥当性評価

### 7. 仮説生成・追加質問
初回分析結果から仮説を立て、検証のための追加質問を生成。

### 8. 仮説検証インタビュー
追加質問による深掘りインタビューで仮説を検証。

### 9. 最終マーケティング戦略分析
全インタビュー結果を統合し、包括的なマーケティング戦略を提案。

### 10. 結果保存・閲覧
- 分析結果の履歴保存
- 過去の結果一覧表示・詳細閲覧
- レポートのダウンロード機能

## 🔧 API エンドポイント

### ペルソナ関連
- `POST /api/generate-personas` - プロジェクト情報に基づくペルソナ生成
- `POST /api/select-personas` - ペルソナ選択

### インタビュー関連
- `GET /api/default-questions` - デフォルト質問取得（商品・競合情報反映）
- `POST /api/conduct-interview` - インタビュー実行
- `POST /api/conduct-hypothesis-interview` - 仮説検証インタビュー

### 分析関連
- `POST /api/generate-analysis` - 初回インサイト分析生成
- `POST /api/generate-hypothesis` - 仮説と追加質問生成
- `POST /api/generate-final-analysis` - 最終マーケティング戦略分析

### データ連携関連
- `POST /api/upload-excel-questions` - Excelファイルから質問読み取り
- `POST /api/save-interview-history` - インタビュー結果の履歴保存
- `GET /api/interview-history` - 過去の履歴一覧取得
- `GET /api/interview-history/{history_id}` - 特定履歴の詳細取得

### セッション関連
- `GET /api/session-status` - セッション状態取得

## 🎨 UI/UX 特徴

- **レスポンシブデザイン**: モバイル・タブレット・デスクトップ対応
- **プログレス表示**: 9ステップのワークフローを視覚化
- **誘導入力**: 商品・サービス情報の体系的入力ガイド
- **リアルタイムフィードバック**: ローディング状態とエラーハンドリング
- **インタラクティブカード**: ペルソナ選択やインタビュー結果の表示
- **ファイルアップロード**: Excelファイルからの質問読み取り機能
- **履歴管理**: 過去の結果の保存・閲覧インターフェース
- **アクセシビリティ**: キーボードナビゲーションとスクリーンリーダー対応

## 📊 技術スタック

### バックエンド
- **FastAPI**: 高性能Pythonフレームワーク
- **Google Generative AI**: Gemini APIを使用したテキスト生成
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGIサーバー
- **Pandas**: Excelファイル読み取り・データ処理
- **OpenPyXL**: Excel (.xlsx) ファイル対応

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

#### 方法1: 改善版ランチャー（推奨）
```bash
python3 start-improved.py
```
- 依存関係の自動インストール
- 既存プロセスの自動終了
- エラーハンドリング強化
- ブラウザ自動起動

#### 方法2: Webアプリとして起動
```bash
python3 start-web.py
```
- ブラウザで自動的に開きます
- Electronの問題を回避できます
- 安定した動作

#### 方法3: デスクトップアプリとして起動
```bash
python3 start-desktop.py
```
- 別ウィンドウで起動
- Electronライブラリが必要

#### 方法4: Docker使用
```bash
docker-compose up --build
```