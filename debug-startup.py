#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起動問題デバッグスクリプト
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_processes():
    """現在動いているプロセスを確認"""
    print("🔍 現在動いているプロセス確認")
    print("-" * 50)
    
    # uvicornプロセス確認
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        uvicorn_processes = [line for line in result.stdout.split('\n') if 'uvicorn' in line]
        
        if uvicorn_processes:
            print("✅ uvicornプロセス発見:")
            for proc in uvicorn_processes:
                print(f"   {proc}")
        else:
            print("❌ uvicornプロセスが見つかりません")
    except Exception as e:
        print(f"プロセス確認エラー: {e}")
    
    # ポート確認
    try:
        result = subprocess.run(['netstat', '-tlpn'], capture_output=True, text=True)
        port_8000 = [line for line in result.stdout.split('\n') if ':8000' in line]
        
        if port_8000:
            print("✅ ポート8000で何かがリスニング中:")
            for line in port_8000:
                print(f"   {line}")
        else:
            print("❌ ポート8000でリスニングしているプロセスなし")
    except Exception as e:
        print(f"ポート確認エラー: {e}")

def test_backend_direct():
    """バックエンドに直接接続テスト"""
    print("\n🔍 バックエンド直接接続テスト")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ バックエンド応答: {response.status_code}")
        print(f"   応答内容: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print("❌ バックエンドに接続できません (CONNECTION_REFUSED)")
    except requests.exceptions.Timeout:
        print("❌ バックエンド接続タイムアウト")
    except Exception as e:
        print(f"❌ バックエンド接続エラー: {e}")

def start_backend_manually():
    """バックエンドを手動で起動してテスト"""
    print("\n🚀 バックエンドを手動起動してテスト")
    print("-" * 50)
    
    backend_dir = Path("/home/kyosuke/marketing-interview-app/backend")
    
    try:
        print("📍 バックエンドディレクトリに移動...")
        import os
        os.chdir(backend_dir)
        
        print("🚀 uvicornでバックエンドを起動中...")
        
        # バックエンドプロセスを起動
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "localhost", "--port", "8000"
        ])
        
        print("⏳ 5秒待機...")
        time.sleep(5)
        
        # 接続テスト
        print("🔍 接続テスト実行...")
        test_backend_direct()
        
        # プロセス終了
        print("🛑 テスト完了、プロセスを終了...")
        backend_process.terminate()
        backend_process.wait()
        
    except Exception as e:
        print(f"❌ 手動起動エラー: {e}")

def check_env():
    """環境変数確認"""
    print("\n🔍 環境設定確認")
    print("-" * 50)
    
    env_file = Path("/home/kyosuke/marketing-interview-app/.env")
    if env_file.exists():
        print("✅ .envファイル存在")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0] if '=' in line else line.strip()
                    if 'API_KEY' in key:
                        print(f"   {key}=***設定済み***")
                    else:
                        print(f"   {line.strip()}")
    else:
        print("❌ .envファイルが見つかりません")

if __name__ == "__main__":
    print("🔧 起動問題デバッグ診断")
    print("=" * 60)
    
    check_env()
    check_processes()
    test_backend_direct()
    start_backend_manually()
    
    print("\n📋 診断完了")
