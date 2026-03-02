# AI Interview - 開発状況ドキュメント

> **最終更新**: 2026-03-02  
> **目的**: このファイルをAIに読み込ませることで、プロジェクトの全体像と現状を即座に把握できるようにする。

---

## 1. プロジェクト概要

| 項目 | 内容 |
|------|------|
| **プロダクト名** | AI Interview（tames プロダクトファミリー） |
| **目的** | LLMで仮想ペルソナを生成し、定性インタビューを実施してマーケティングインサイトを得る |
| **姉妹サイト** | AI Survey（定量調査）: `https://tames-frontend-staging-128899916170.asia-northeast1.run.app/` |
| **リポジトリ** | `https://github.com/kumakyo/marketing-interview-app.git` |
| **ブランチ** | `main`（単一ブランチ運用） |
| **最新コミット** | (後述の Git 履歴参照) |

---

## 2. 技術スタック

### バックエンド
| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11 (Docker) / 3.9 (backend/Dockerfile) | ランタイム |
| FastAPI | 0.115.5 | Web フレームワーク |
| Vertex AI SDK (`google-cloud-aiplatform`) | >=1.38.0 | LLM（ペルソナ生成・インタビュー・分析）。GCP課金経由 |
| SQLAlchemy | 2.0.25 | ORM |
| SQLite / PostgreSQL | - | データベース（ローカル: SQLite、Cloud Run: PostgreSQL） |
| python-jose | 3.5.0 | JWT 検証 |
| slowapi | latest | レート制限（60リクエスト/分/IP） |
| python-pptx | latest | PowerPoint レポート生成 |
| matplotlib | latest | PPTX 内グラフ生成 |

### フロントエンド
| 技術 | バージョン | 用途 |
|------|-----------|------|
| Next.js | 15.1.3 | React フレームワーク |
| React | 18.2.0 | UI ライブラリ |
| NextAuth.js | 4.24.13 | Google OAuth 認証 |
| Tailwind CSS | 4 | スタイリング |
| Axios | 1.6.0 | HTTP クライアント |
| TypeScript | 5 | 型安全 |

### インフラ
| 技術 | 用途 |
|------|------|
| GCP Cloud Run | バックエンド・フロントエンドホスティング |
| GCP Cloud SQL (PostgreSQL) | 本番データベース（`work-487701:asia-northeast1:marketing-db`） |
| GCP Artifact Registry | Docker イメージ管理（`marketing-repo`） |
| Docker | コンテナ化 |

---

## 3. ディレクトリ構成

```
marketing-interview/
├── Dockerfile                  # Cloud Run バックエンド用（Python 3.11-slim）
├── .gitignore
├── .env                        # ローカル環境変数（Git 管理外）
├── README.md
├── requirements.txt            # ルート用依存関係
│
├── backend/
│   ├── Dockerfile              # バックエンド用（Python 3.9-slim）
│   ├── requirements.txt        # バックエンド依存関係
│   ├── main.py                 # FastAPI メインアプリ（2,226行）
│   ├── auth.py                 # JWT 認証ミドルウェア
│   ├── database.py             # SQLAlchemy モデル定義
│   ├── db_manager.py           # DB 操作ヘルパー
│   ├── pptx_generator.py       # PowerPoint レポート生成
│   └── update_sessions.py      # セッション更新ユーティリティ
│
├── frontend/
│   ├── Dockerfile              # Cloud Run フロントエンド用（マルチステージ）
│   ├── package.json
│   ├── next.config.ts          # Next.js 設定（standalone 出力、CORS ヘッダー）
│   ├── .dockerignore           # Docker ビルド時に .env* 等を除外
│   └── src/
│       ├── app/
│       │   ├── page.tsx        # メインアプリ画面（1,609行、4ステップ管理）
│       │   ├── layout.tsx      # ルートレイアウト
│       │   ├── globals.css     # グローバルスタイル
│       │   ├── providers.tsx   # NextAuth SessionProvider
│       │   ├── auth/signin/page.tsx  # ログインページ
│       │   └── api/auth/[...nextauth]/route.ts  # NextAuth API ルート
│       ├── components/
│       │   ├── Sidebar.tsx                    # 左サイドバー（AI Survey 統一デザイン）
│       │   ├── ComprehensiveAnalysisView.tsx   # 分析結果タブ表示
│       │   ├── ChatPersonaCard.tsx             # ペルソナ選択カード
│       │   ├── ChatInterview.tsx               # チャット形式インタビュー
│       │   ├── ChatStyleInterview.tsx          # LINE 風チャット表示
│       │   ├── ProductServiceForm.tsx          # 商品サービス入力フォーム
│       │   ├── CompetitorForm.tsx              # 競合情報入力フォーム
│       │   ├── InterviewResults.tsx            # インタビュー結果表示
│       │   ├── InsightAnalysis.tsx             # インサイト分析表示
│       │   ├── PsychologyAnalysis.tsx          # 深層心理分析
│       │   ├── PersonaCard.tsx                 # ペルソナカード
│       │   ├── LoadingSpinner.tsx              # ローディング
│       │   └── ...
│       ├── lib/
│       │   └── api.ts          # API クライアント（axios + JWT 自動付与）
│       └── types/
│           └── next-auth.d.ts  # NextAuth 型定義拡張
│
├── scripts/
│   └── deploy-cloudrun.sh      # Cloud Run デプロイスクリプト
│
├── original_script/            # 元の Python スクリプト（CLI 版）
│   ├── marketing_interview.py
│   └── ...
│
└── 参考/                        # UI/UX 参考スクリーンショット（AI Survey）
    └── *.png
```

---

## 4. アプリケーションフロー

### 4.1 認証フロー

```
ユーザー → Google OAuth → NextAuth → カスタム JWT 生成（HS256）
                                        ↓
                              session.backendToken に格納
                                        ↓
                              axios インターセプター → Authorization: Bearer <JWT>
                                        ↓
                              backend/auth.py → JWT 検証 → User 取得
```

### 4.2 インタビューフロー（4ステップ）

```
Step 0: プロジェクト設定
  ├── トピック入力
  ├── 商品・サービス情報（名前, ターゲット, ベネフィット, 根拠, 基本情報）
  ├── 競合情報（任意）
  ├── 分析目的選択（市場構造 / 消費者ニーズ / 商品改善）
  ├── ペルソナ人数設定（3〜15人）
  └── [ペルソナ生成] → Gemini API

Step 1: ペルソナ選択
  └── 生成されたペルソナからインタビュー対象者を選択

Step 2: 質問作成
  ├── AI 自動生成質問（トピック特化）
  ├── Excel アップロード
  └── 手動編集

Step 3: 分析結果表示（自動一括実行）
  ├── 初回インタビュー実行
  ├── インタビューサマリ生成
  ├── 初回インサイト分析
  ├── 仮説と追加質問生成
  ├── 仮説検証インタビュー
  ├── カスタム最終分析（選択した分析タイプに基づく）
  └── ComprehensiveAnalysisView で表示
       ├── サマリタブ
       ├── インサイトタブ
       ├── ペルソナ別詳細タブ
       ├── [追加質問インタビュー] 実行可能
       └── [PowerPoint ダウンロード]
```

---

## 5. API エンドポイント一覧

| メソッド | パス | 概要 |
|----------|------|------|
| GET | `/` | ヘルスチェック |
| POST | `/api/auth/google-signin` | Google 認証後ユーザー登録・更新 |
| GET | `/api/auth/me` | 現在のユーザー情報取得 |
| GET | `/api/user/projects` | ユーザープロジェクト一覧 |
| GET | `/api/user/statistics` | ユーザー統計 |
| GET | `/api/input-history` | 入力履歴 |
| POST | `/api/generate-personas` | ペルソナ生成 |
| POST | `/api/set-analysis-types` | 分析タイプ設定 |
| POST | `/api/select-personas` | ペルソナ選択 |
| GET | `/api/default-questions` | デフォルト質問取得 |
| POST | `/api/conduct-interview` | インタビュー実行 |
| POST | `/api/generate-analysis` | 初回インサイト分析 |
| POST | `/api/generate-hypothesis` | 仮説・追加質問生成 |
| POST | `/api/conduct-hypothesis-interview` | 仮説検証インタビュー |
| POST | `/api/generate-custom-final-analysis` | カスタム最終分析 |
| POST | `/api/generate-final-analysis` | 最終マーケティング戦略分析 |
| POST | `/api/generate-interview-summary` | インタビューサマリ生成 |
| POST | `/api/export-pptx` | PowerPoint レポート出力 |
| POST | `/api/upload-excel-questions` | Excel 質問アップロード |
| POST | `/api/save-interview-history` | 履歴保存 |
| GET | `/api/interview-history` | 履歴一覧 |
| GET | `/api/interview-history/{id}` | 履歴詳細 |
| GET | `/api/session-status` | セッション状態 |
| POST | `/api/analyze-psychology` | 深層心理分析 |

---

## 6. データベースモデル

| テーブル | 主なカラム | 概要 |
|----------|------------|------|
| **users** | id, email, name, picture, created_at | ユーザー |
| **projects** | id, user_id, topic, products_services(JSON), competitors(JSON), analysis_types(JSON) | プロジェクト |
| **personas** | id, project_id, name, details(JSON), raw_text, index_order | ペルソナ |
| **interviews** | id, project_id, persona_id, questions(JSON), results(JSON), is_hypothesis_phase | インタビュー結果 |
| **analyses** | id, project_id, analysis_type, content | 分析結果 |
| **interview_sessions** | id, user_id, project_id, state(JSON) | セッション状態 |

---

## 7. セキュリティ実装状況

| 項目 | 状態 | 詳細 |
|------|------|------|
| Google OAuth | 完了 | NextAuth.js + Google Provider |
| JWT 認証 | 完了 | HS256、NEXTAUTH_SECRET で署名・検証 |
| CORS | 完了 | 環境変数 `CORS_ALLOWED_ORIGINS` で制御 |
| レート制限 | 完了 | slowapi: 60リクエスト/分/IP |
| .gitignore | 完了 | .env, .env.backup*, setup-oauth-env* を除外 |
| .dockerignore | 完了 | `.env*` をDockerビルドから除外（env漏洩防止） |

---

## 8. UI/UX デザイン

### デザインコンセプト
AI Survey（定量サイト）と統一したデザイン。白ベース、青(#2563eb)プライマリカラー、左サイドバーレイアウト。

### 主要コンポーネント
| コンポーネント | 概要 |
|---------------|------|
| `Sidebar.tsx` | 固定左サイドバー（w-56）。ナビ、ユーザー情報、ステータスドット |
| `globals.css` | CSS 変数によるデザインシステム。`btn-primary`, `btn-secondary`, `card` クラス |
| ログインページ | サイドバー + 中央ログインカード（Google ログイン + 装飾メール/パスワード欄） |
| ホーム画面 | 機能カード4枚グリッド + プロジェクト設定フォーム |

### カラーパレット
```css
--background: #f8fafc;
--foreground: #1a1a2e;
--primary: #2563eb;
--primary-dark: #1d4ed8;
--border: #e5e7eb;
--muted: #6b7280;
--success: #10b981;
--error: #ef4444;
```

---

## 9. デプロイ

### ローカル開発
```bash
# バックエンド
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# フロントエンド
cd frontend && npm install && npm run dev
```

### Cloud Run デプロイ（本番環境）

| サービス | URL | 認証 |
|----------|-----|------|
| フロントエンド | `https://frontend-591352320240.asia-northeast1.run.app` | 不要（公開） |
| バックエンド | `https://backend-591352320240.asia-northeast1.run.app` | 不要（公開） |

**GCP プロジェクト**: `work-487701`  
**リージョン**: `asia-northeast1`  
**Artifact Registry**: `asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/`

#### デプロイ手順（手動）
```bash
# バックエンド
cd backend
docker build -t asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/backend:latest .
docker push asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/backend:latest
gcloud run deploy backend --image asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/backend:latest --region asia-northeast1 --add-cloudsql-instances work-487701:asia-northeast1:marketing-db --allow-unauthenticated

# フロントエンド
cd frontend
docker build --build-arg NEXT_PUBLIC_API_URL=https://backend-591352320240.asia-northeast1.run.app -t asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/frontend:latest .
docker push asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/frontend:latest
gcloud run deploy frontend --image asia-northeast1-docker.pkg.dev/work-487701/marketing-repo/frontend:latest --region asia-northeast1 --allow-unauthenticated
```

**重要**: フロントエンドの `.dockerignore` に `.env*` を含めること（ビルド時にローカル env が混入するバグを防止）

### 必要な環境変数
| 変数名 | 用途 | 設定場所 |
|--------|------|----------|
| `GCP_PROJECT_ID` | Vertex AI プロジェクト ID | Cloud Run 環境変数 |
| `GCP_LOCATION` | Vertex AI リージョン（`us-central1` 推奨） | Cloud Run 環境変数 |
| `GOOGLE_CLIENT_ID` | Google OAuth クライアント ID | .env / Secret Manager |
| `GOOGLE_CLIENT_SECRET` | Google OAuth クライアントシークレット | .env / Secret Manager |
| `NEXTAUTH_SECRET` | JWT 署名用シークレット | .env / Secret Manager |
| `NEXTAUTH_URL` | NextAuth コールバック URL | .env / Cloud Run 環境変数 |
| `NEXT_PUBLIC_API_URL` | バックエンド API URL | .env / Cloud Run ビルド引数 |
| `DATABASE_URL` | PostgreSQL 接続文字列（Cloud Run 用） | Secret Manager |
| `CORS_ALLOWED_ORIGINS` | CORS 許可オリジン（カンマ区切り） | Cloud Run 環境変数 |
| `NEXT_PUBLIC_QUANTITATIVE_URL` | AI Survey へのリンク URL | .env |

---

## 10. 既知の課題・改善点

| カテゴリ | 内容 | 優先度 |
|----------|------|--------|
| ルート | ルートに開発用 Python スクリプトが多数残存（start-*.py, debug-*.py 等）。整理が必要 | 低 |
| バックエンド | `backend/main.py` が 2,226 行と巨大。ルーター分割を検討 | 中 |
| テスト | 自動テスト未実装 | 中 |
| DB | ローカルは SQLite、本番は PostgreSQL。マイグレーション戦略が未定義 | 中 |
| UI | Electron 関連コード（electron/main.js, preload.js）が残存。Web 専用なら削除可 | 低 |
| PPTX | PowerPoint 出力のデザイン・内容の品質向上余地あり | 低 |
| セキュリティ | バックエンドが `--allow-unauthenticated`。IAM 制限を検討 | 中 |

---

## 11. Git 履歴（直近10コミット）

```
796392d Consolidate next.config.ts, remove next.config.js for Cloud Run deployment
27b3a4d Add development status document for AI context sharing
e39e1c6 UI polish: home cards, consistent button styles, clean form sections matching AI Survey
956fe50 Full rebuild: auth, sidebar UI, PPTX export, security hardening, design matching AI Survey
d4ca49b Initial commit: tames interview - AIマーケティングインタビューシステム
27d67e4 分析タイプ選択UI追加とデバッグ修正
42cbe0a 分析タイプ選択と用語修正
afc1a18 分析タイプ選択をプロジェクト設定ページに統合
9d9f4a5 UI改善とフロー最適化
e68a6e2 大幅機能改善: 分析タイプ選択、用語変更、可変人数対応
```

---

## 12. 主要ファイルの行数

| ファイル | 行数 | 役割 |
|----------|------|------|
| `backend/main.py` | 2,226 | 全 API エンドポイント |
| `frontend/src/app/page.tsx` | 1,609 | メイン画面（4ステップ） |
| `backend/pptx_generator.py` | 484 | PPTX レポート生成 |
| `frontend/src/lib/api.ts` | 370 | API クライアント（Bearer JWT 自動付与、withCredentials 不使用） |
| `frontend/src/components/ComprehensiveAnalysisView.tsx` | 261 | 分析結果表示 |
| `backend/db_manager.py` | 210 | DB 操作 |
| `frontend/src/app/auth/signin/page.tsx` | 190 | ログインページ |
| `backend/database.py` | 157 | DB モデル |
| `frontend/src/components/Sidebar.tsx` | 155 | 左サイドバー |
| `backend/auth.py` | 101 | JWT 認証 |

---

## 13. デプロイ済み Cloud Run 環境変数

### バックエンド (`backend`)
| 変数名 | 設定済み | 備考 |
|--------|---------|------|
| `DATABASE_URL` | Yes | Cloud SQL 経由 (`/cloudsql/work-487701:asia-northeast1:marketing-db`) |
| `GOOGLE_API_KEY` | 不要 | Vertex AI SDK に切替済み。サービスアカウント (ADC) で認証 |
| `GCP_PROJECT_ID` | Yes | `work-487701` |
| `GCP_LOCATION` | Yes | `us-central1`（Gemini モデルは asia-northeast1 非対応のため） |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth 2.0 |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth 2.0 |
| `NEXTAUTH_SECRET` | Yes | JWT 署名検証用 |
| `CORS_ALLOWED_ORIGINS` | Yes | `https://frontend-591352320240.asia-northeast1.run.app` |

### フロントエンド (`frontend`)
| 変数名 | 設定済み | 備考 |
|--------|---------|------|
| `NEXT_PUBLIC_API_URL` | Yes | ビルド引数 + ランタイム env |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth 2.0 |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth 2.0 |
| `NEXTAUTH_URL` | Yes | `https://frontend-591352320240.asia-northeast1.run.app` |
| `NEXTAUTH_SECRET` | Yes | JWT 署名用 |

---

## 14. 解決済みバグ・トラブルシューティング

| 日付 | 問題 | 原因 | 対処 |
|------|------|------|------|
| 2026-03-02 | `Cannot read properties of undefined (reading 'startsWith')` | `.dockerignore` が `.env*` を除外していなかったため、ローカルの `.env.production`（古いURL）がDockerビルドに混入。`api.ts` の `API_BASE_URL.startsWith()` が undefined で失敗 | `.dockerignore` に `.env*` 追加、`api.ts` 簡素化、`withCredentials: true` 削除 |
| 2026-03-02 | ペルソナ生成失敗（API キー） | バックエンドの `GOOGLE_API_KEY` が古い無効なキーだった | Cloud Run env var を新しい API キーに更新 |
| 2026-03-02 | 429 Quota exceeded (Free Tier) | `google-generativeai` (AI Studio SDK) は Free Tier 制限（10 req/min）が適用される | `google-cloud-aiplatform` (Vertex AI SDK) に切替。GCP 課金（無料トライアル含む）経由でレート制限大幅緩和。Vertex AI API 有効化 + サービスアカウントに `aiplatform.user` ロール付与 |
| 2026-03-02 | 404 Publisher Model not found | `gemini-2.5-flash-lite` は `asia-northeast1` で Vertex AI 非対応 | `GCP_LOCATION` を `us-central1` に変更（Cloud Run は `asia-northeast1` のまま） |
| 2026-03-02 | Git push blocked (GH013) | 過去コミットに Google OAuth Client ID/Secret が含まれていた | `git reset --soft origin/main` で履歴をクリーンアップし再コミット |
