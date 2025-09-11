#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接続問題のデバッグツール
"""

import sys
import subprocess
import time
import os
from pathlib import Path

APP_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = APP_DIR / "backend"

def test_backend_connection():
    """バックエンドの接続をテスト"""
    print("🔍 バックエンド接続テスト")
    
    try:
        import requests
    except ImportError:
        print("📦 requestsライブラリをインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        import requests
    
    # バックエンドを一時的に起動してテスト
    print("🚀 バックエンドサーバーを起動中...")
    
    # 環境変数の設定
    env = os.environ.copy()
    env_file = APP_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    env[key] = value
    
    try:
        os.chdir(BACKEND_DIR)
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "localhost", "--port", "8000"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # サーバーの起動を待つ
        print("⏳ サーバー起動を待機中...")
        time.sleep(5)
        
        # 接続テスト
        test_urls = [
            "http://localhost:8000/",
            "http://localhost:8000/api/session-status",
            "http://localhost:8000/api/default-questions"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {url}: OK")
                else:
                    print(f"❌ {url}: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {url}: 接続エラー - {e}")
        
        # API Docsのテスト
        try:
            response = requests.get("http://localhost:8000/docs", timeout=10)
            if response.status_code == 200:
                print("✅ API ドキュメント: http://localhost:8000/docs")
            else:
                print(f"❌ API ドキュメント: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ API ドキュメント: 接続エラー - {e}")
        
        # プロセス終了
        backend_process.terminate()
        backend_process.wait(timeout=5)
        
        print("\n✅ バックエンド接続テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ バックエンドテストエラー: {e}")
        return False

def check_ports():
    """ポート使用状況をチェック"""
    print("\n🔍 ポート使用状況チェック")
    
    ports = [3000, 3001, 8000]
    
    for port in ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"❌ ポート {port}: 使用中")
            else:
                print(f"✅ ポート {port}: 使用可能")
        except Exception as e:
            print(f"❓ ポート {port}: チェック不可 - {e}")

def show_process_info():
    """プロセス情報を表示"""
    print("\n🔍 関連プロセス情報")
    
    try:
        # Node.jsプロセス
        result = subprocess.run(['pgrep', '-f', 'node'], capture_output=True, text=True)
        if result.stdout.strip():
            print("📱 Node.jsプロセス:")
            for pid in result.stdout.strip().split('\n'):
                if pid.strip():
                    try:
                        ps_result = subprocess.run(['ps', '-p', pid.strip(), '-o', 'pid,cmd'], 
                                                 capture_output=True, text=True)
                        print(f"   {ps_result.stdout.strip()}")
                    except Exception:
                        pass
        else:
            print("📱 Node.jsプロセス: なし")
        
        # Pythonプロセス（uvicorn）
        result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
        if result.stdout.strip():
            print("🐍 Uvicornプロセス:")
            for pid in result.stdout.strip().split('\n'):
                if pid.strip():
                    try:
                        ps_result = subprocess.run(['ps', '-p', pid.strip(), '-o', 'pid,cmd'], 
                                                 capture_output=True, text=True)
                        print(f"   {ps_result.stdout.strip()}")
                    except Exception:
                        pass
        else:
            print("🐍 Uvicornプロセス: なし")
            
    except Exception as e:
        print(f"❌ プロセス情報の取得エラー: {e}")

def main():
    print("🔧 マーケティングインタビューシステム 接続デバッグ")
    print("=" * 60)
    
    # ポートチェック
    check_ports()
    
    # プロセス情報
    show_process_info()
    
    # バックエンド接続テスト
    backend_ok = test_backend_connection()
    
    print("\n" + "=" * 60)
    print("📊 診断結果:")
    
    if backend_ok:
        print("✅ バックエンド: 正常")
        print("\n💡 推奨アクション:")
        print("   1. python3 start-web.py でアプリを起動")
        print("   2. ブラウザで http://localhost:3000 または http://localhost:3001 を開く")
    else:
        print("❌ バックエンド: 問題あり")
        print("\n💡 推奨アクション:")
        print("   1. .envファイルでGOOGLE_API_KEYを設定")
        print("   2. python3 start-web.py でアプリを再起動")
        print("   3. ブラウザのコンソールでエラーを確認")
    
    return 0 if backend_ok else 1

if __name__ == "__main__":
    sys.exit(main())
