# Google認証実装ガイド

このドキュメントでは、Google認証を実装し、ユーザー別のデータ管理を行うための手順を説明します。

## 📋 実装する機能

1. **Googleアカウント認証**
   - Google OAuth 2.0を使用したログイン
   - NextAuth.jsによるセッション管理

2. **ユーザー別データ管理**
   - インタビュー結果をユーザーごとに保存
   - SQLiteデータベースでの永続化
   - 他のユーザーのデータへのアクセス制限

3. **履歴管理**
   - ログインユーザーの過去の実行結果を表示
   - 詳細な履歴閲覧機能

## 🔧 必要な設定

### 1. Google Cloud Console設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. 「APIとサービス」→「認証情報」に移動
4. 「認証情報を作成」→「OAuth クライアント ID」を選択
5. アプリケーションの種類: 「ウェブアプリケーション」を選択
6. 承認済みのリダイレクトURIを追加：
   ```
   http://localhost:3001/api/auth/callback/google
   https://localhost:3001/api/auth/callback/google
   ```
7. クライアントIDとクライアントシークレットをコピー

### 2. 環境変数の設定

プロジェクトルートの `.env` ファイルに以下を追加：

```bash
# Google OAuth 2.0
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here

# NextAuth
NEXTAUTH_URL=https://localhost:3001
NEXTAUTH_SECRET=your_random_secret_key_here

# 既存のGemini API Key
GOOGLE_API_KEY=AIzaSyBG5sSBZqm14RY2JMob_zPUDqhw4sRNEXg
```

フロントエンドの `.env.local` ファイルに以下を追加：

```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
NEXTAUTH_URL=https://localhost:3001
NEXTAUTH_SECRET=your_random_secret_key_here
NEXT_PUBLIC_API_URL=https://localhost:8000
NODE_TLS_REJECT_UNAUTHORIZED=0
```

### 3. NEXTAUTHシークレットの生成

```bash
openssl rand -base64 32
```

このコマンドで生成された文字列を `NEXTAUTH_SECRET` に設定してください。

## 📁 実装済みファイル

### フロントエンド

1. **`frontend/src/app/api/auth/[...nextauth]/route.ts`**
   - NextAuth.jsの設定
   - Google認証プロバイダーの設定
   - JWTコールバックの実装

2. **`frontend/src/types/next-auth.d.ts`**
   - TypeScript型定義
   - セッション型の拡張

3. **`frontend/src/app/auth/signin/page.tsx`**
   - ログインページのUI
   - Googleログインボタン

## 🚀 次のステップ（未実装）

### バックエンド実装

1. **`backend/auth.py`** - JWT認証ミドルウェア（作成必要）
2. **`backend/database.py`** - SQLiteデータベース管理（作成必要）
3. **`backend/main.py`** - 認証とデータベース統合（更新必要）

### フロントエンド実装

1. **`frontend/src/app/layout.tsx`** - SessionProviderの追加（更新必要）
2. **`frontend/src/app/page.tsx`** - 認証チェックの追加（更新必要）
3. **`frontend/src/components/AuthGuard.tsx`** - 認証ガード（作成必要）
4. **`frontend/src/lib/api.ts`** - 認証ヘッダーの追加（更新必要）

## 📝 実装手順（詳細）

### ステップ1: 環境変数設定

1. Google Cloud ConsoleでOAuth 2.0クライアントIDを作成
2. `.env`ファイルと`.env.local`ファイルに認証情報を追加
3. NEXTAUTHシークレットを生成して設定

### ステップ2: バックエンド認証実装

#### `backend/auth.py`を作成：

```python
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from typing import Optional

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="認証が必要です")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="無効なトークン")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="無効なトークン")
```

#### `backend/database.py`を作成：

```python
import sqlite3
import json
from datetime import datetime
from typing import List, Optional

class Database:
    def __init__(self, db_path="data/interviews.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ユーザーテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # インタビュー履歴テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                project_info TEXT NOT NULL,
                analysis TEXT,
                final_analysis TEXT,
                hypothesis_and_questions TEXT,
                personas_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_interview(self, user_id, interview_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interview_history 
            (id, user_id, topic, project_info, analysis, final_analysis, 
             hypothesis_and_questions, personas_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interview_data['id'],
            user_id,
            interview_data['topic'],
            json.dumps(interview_data['project_info']),
            interview_data.get('analysis', ''),
            interview_data.get('final_analysis', ''),
            interview_data.get('hypothesis_and_questions', ''),
            json.dumps(interview_data.get('personas_used', [])),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_history(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM interview_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
```

#### `backend/main.py`を更新：

```python
# インポートに追加
from fastapi import Depends
from auth import verify_token
from database import Database

# データベース初期化
db = Database()

# エンドポイントに認証を追加
@app.post("/api/save-interview-history")
async def save_interview_history(user_id: str = Depends(verify_token)):
    # user_idを使用してデータを保存
    ...
```

### ステップ3: フロントエンド認証統合

#### `frontend/src/app/layout.tsx`を更新：

```typescript
import { SessionProvider } from "next-auth/react"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>
        <SessionProvider>
          {children}
        </SessionProvider>
      </body>
    </html>
  )
}
```

#### `frontend/src/components/AuthGuard.tsx`を作成：

```typescript
'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  if (!session) {
    return null;
  }

  return <>{children}</>;
}
```

#### `frontend/src/app/page.tsx`を更新：

```typescript
'use client';

import AuthGuard from '@/components/AuthGuard';
import { useSession } from 'next-auth/react';

export default function Home() {
  return (
    <AuthGuard>
      {/* 既存のコンテンツ */}
    </AuthGuard>
  );
}
```

### ステップ4: API通信の更新

#### `frontend/src/lib/api.ts`を更新：

```typescript
import { getSession } from 'next-auth/react';

class APIClient {
  private async getHeaders() {
    const session = await getSession();
    return {
      'Content-Type': 'application/json',
      ...(session?.accessToken && {
        'Authorization': `Bearer ${session.accessToken}`
      })
    };
  }

  // 既存のメソッドを更新...
}
```

## ✅ テスト手順

1. Google Cloud Consoleで認証情報を設定
2. 環境変数ファイルを更新
3. アプリケーションを再起動
4. `https://localhost:3001`にアクセス
5. ログイン画面が表示されることを確認
6. Googleでログイン
7. インタビューを実行
8. 履歴が保存されることを確認
9. ログアウトして再ログイン
10. 履歴が表示されることを確認

## 🔒 セキュリティ考慮事項

1. **環境変数の管理**
   - `.env`ファイルをGitに含めない
   - 本番環境では環境変数を安全に管理

2. **JWT検証**
   - すべての保護されたエンドポイントでトークンを検証
   - トークンの有効期限を設定

3. **データアクセス制御**
   - ユーザーIDで厳密にデータを分離
   - SQLインジェクション対策

4. **HTTPS通信**
   - 本番環境では必ず正式な証明書を使用
   - 自己署名証明書は開発環境のみ

## 📚 参考リンク

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**注意**: この実装を完了するには、上記の「次のステップ」セクションの未実装部分を完成させる必要があります。

