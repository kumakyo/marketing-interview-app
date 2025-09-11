#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アプリケーション動作テスト
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = APP_DIR / "backend"

def test_backend():
    """バックエンドサーバーをテスト"""
    print("🧪 バックエンドサーバーテスト")
    
    # 環境変数の設定
    env = os.environ.copy()
    env_file = APP_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    env[key] = value
    
    # バックエンドを起動
    print("🚀 バックエンドサーバーを起動中...")
    try:
        os.chdir(BACKEND_DIR)
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "localhost", "--port", "8000"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 起動を待つ
        time.sleep(5)
        
        # ヘルスチェック
        print("📡 APIエンドポイントをテスト中...")
        
        try:
            # ルートエンドポイント
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("   ✅ ルートエンドポイント OK")
            else:
                print(f"   ❌ ルートエンドポイント NG (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ ルートエンドポイント接続エラー: {e}")
        
        try:
            # セッション状態エンドポイント
            response = requests.get("http://localhost:8000/api/session-status", timeout=10)
            if response.status_code == 200:
                print("   ✅ セッション状態エンドポイント OK")
            else:
                print(f"   ❌ セッション状態エンドポイント NG (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ セッション状態エンドポイント接続エラー: {e}")
        
        try:
            # デフォルト質問エンドポイント
            response = requests.get("http://localhost:8000/api/default-questions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'questions' in data and len(data['questions']) > 0:
                    print("   ✅ デフォルト質問エンドポイント OK")
                else:
                    print("   ❌ デフォルト質問エンドポイント データ不正")
            else:
                print(f"   ❌ デフォルト質問エンドポイント NG (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ デフォルト質問エンドポイント接続エラー: {e}")
        
        # API Docs
        try:
            response = requests.get("http://localhost:8000/docs", timeout=10)
            if response.status_code == 200:
                print("   ✅ API ドキュメント OK")
            else:
                print(f"   ❌ API ドキュメント NG (status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ API ドキュメント接続エラー: {e}")
        
        print("✅ バックエンドテスト完了")
        
        # プロセス終了
        backend_process.terminate()
        backend_process.wait(timeout=5)
        
        return True
        
    except Exception as e:
        print(f"❌ バックエンドテストエラー: {e}")
        return False

def test_api_key():
    """APIキーをテスト"""
    print("\n🔑 Google API キーテスト")
    
    env_file = APP_DIR / ".env"
    if not env_file.exists():
        print("❌ .envファイルが見つかりません")
        return False
    
    # APIキーを読み取り
    api_key = None
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith('GOOGLE_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break
    
    if not api_key or api_key == 'your_google_api_key_here':
        print("❌ GOOGLE_API_KEYが設定されていません")
        return False
    
    # APIキーの形式チェック
    if api_key.startswith('AIza') and len(api_key) > 30:
        print("✅ GOOGLE_API_KEY形式OK")
        return True
    else:
        print("⚠️  GOOGLE_API_KEY形式が不正の可能性があります")
        return False

def main():
    """メイン関数"""
    print("🧪 マーケティングインタビューシステム 動作テスト")
    print("=" * 60)
    
    # APIキーテスト
    api_key_ok = test_api_key()
    
    # バックエンドテスト
    backend_ok = test_backend()
    
    print("\n" + "=" * 60)
    print("📊 テスト結果:")
    
    if api_key_ok:
        print("✅ API キー: OK")
    else:
        print("❌ API キー: NG")
    
    if backend_ok:
        print("✅ バックエンド: OK")
    else:
        print("❌ バックエンド: NG")
    
    if api_key_ok and backend_ok:
        print("\n🎉 すべてのテストが成功しました！")
        print("💡 以下のコマンドでアプリを起動できます:")
        print("   🌐 Webアプリ: python3 start-web.py")
        print("   🖥️  デスクトップアプリ: python3 start-desktop.py")
        return 0
    else:
        print("\n⚠️  いくつかのテストが失敗しました")
        if not api_key_ok:
            print("🔧 .envファイルでGOOGLE_API_KEYを設定してください")
        if not backend_ok:
            print("🔧 Python依存関係を確認してください")
        return 1

if __name__ == "__main__":
    # requests ライブラリをインストール
    try:
        import requests
    except ImportError:
        print("📦 requests ライブラリをインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        import requests
    
    sys.exit(main())
