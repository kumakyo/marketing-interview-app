#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
フロントエンド・バックエンド接続の詳細診断
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

APP_DIR = Path("/home/kyosuke/marketing-interview-app")
BACKEND_DIR = APP_DIR / "backend"

def test_backend_endpoints():
    """バックエンドエンドポイントを詳細テスト"""
    print("🔍 バックエンドエンドポイント詳細テスト")
    
    # 環境変数を設定
    env = os.environ.copy()
    env_file = APP_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    env[key] = value.strip().strip('"\'')
    
    # バックエンドを一時起動
    print("🚀 バックエンドサーバーを起動中...")
    try:
        os.chdir(BACKEND_DIR)
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "localhost", "--port", "8000"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(5)  # 起動を待つ
        
        # 各エンドポイントをテスト
        endpoints = [
            ("/", "ルートエンドポイント"),
            ("/api/session-status", "セッション状態"),
            ("/api/default-questions", "デフォルト質問"),
            ("/docs", "API ドキュメント"),
        ]
        
        base_url = "http://localhost:8000"
        all_ok = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {name} ({endpoint}): OK")
                    if endpoint == "/api/default-questions":
                        data = response.json()
                        print(f"   📝 質問数: {len(data.get('questions', []))}")
                else:
                    print(f"❌ {name} ({endpoint}): HTTP {response.status_code}")
                    all_ok = False
            except requests.exceptions.RequestException as e:
                print(f"❌ {name} ({endpoint}): 接続エラー - {e}")
                all_ok = False
        
        # CORS ヘッダーをテスト
        print("\n🔍 CORS設定テスト")
        try:
            response = requests.options(f"{base_url}/api/session-status", headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET'
            })
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            print(f"✅ CORS設定: {cors_headers}")
        except Exception as e:
            print(f"❌ CORS設定確認エラー: {e}")
        
        # Google API キーテスト（バックエンド経由）
        print("\n🔍 Google API テスト（バックエンド経由）")
        try:
            # ペルソナ生成APIを少量テスト
            test_data = {"topic": "テスト"}
            response = requests.post(f"{base_url}/api/generate-personas", 
                                   json=test_data, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if 'personas' in data:
                    print("✅ Google API（バックエンド経由）: 正常")
                else:
                    print("❌ Google API（バックエンド経由）: レスポンス形式エラー")
            else:
                print(f"❌ Google API（バックエンド経由）: HTTP {response.status_code}")
                if response.text:
                    print(f"   エラー詳細: {response.text[:200]}...")
        except requests.exceptions.Timeout:
            print("❌ Google API（バックエンド経由）: タイムアウト")
        except Exception as e:
            print(f"❌ Google API（バックエンド経由）: {e}")
        
        # プロセス終了
        backend_process.terminate()
        backend_process.wait(timeout=5)
        
        return all_ok
        
    except Exception as e:
        print(f"❌ バックエンドテストエラー: {e}")
        return False

def check_environment_variables():
    """環境変数を詳細確認"""
    print("\n🔍 環境変数詳細確認")
    
    env_file = APP_DIR / ".env"
    if not env_file.exists():
        print("❌ .envファイルが存在しません")
        return False
    
    print("✅ .envファイル存在")
    
    # .envファイルの内容確認
    with open(env_file, 'r') as f:
        content = f.read()
        
    if 'GOOGLE_API_KEY=' in content:
        # APIキーの確認
        for line in content.split('\n'):
            if line.startswith('GOOGLE_API_KEY='):
                api_key = line.split('=', 1)[1].strip().strip('"\'')
                if api_key and api_key != 'your_google_api_key_here':
                    print(f"✅ GOOGLE_API_KEY: {api_key[:10]}...{api_key[-10:]}")
                    return True
                else:
                    print("❌ GOOGLE_API_KEY: 未設定または無効")
                    return False
    
    print("❌ GOOGLE_API_KEY: 設定なし")
    return False

def main():
    print("🔧 フロントエンド・バックエンド接続診断")
    print("=" * 60)
    
    # 環境変数確認
    env_ok = check_environment_variables()
    
    # バックエンドエンドポイントテスト
    backend_ok = test_backend_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 診断結果:")
    print(f"✅ 環境変数: {'OK' if env_ok else 'NG'}")
    print(f"✅ バックエンド: {'OK' if backend_ok else 'NG'}")
    
    if env_ok and backend_ok:
        print("\n🎉 すべて正常です！")
        print("💡 フロントエンドの問題の可能性:")
        print("   1. ブラウザのキャッシュをクリア")
        print("   2. ブラウザの開発者ツールでネットワークタブを確認")
        print("   3. python3 start-web.py で再起動")
    else:
        print("\n⚠️  問題が検出されました")
        if not env_ok:
            print("🔧 .envファイルでGOOGLE_API_KEYを正しく設定してください")
        if not backend_ok:
            print("🔧 バックエンドサーバーに問題があります")
    
    return 0 if (env_ok and backend_ok) else 1

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("📦 requestsライブラリをインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    sys.exit(main())