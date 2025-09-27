#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - 改善版起動スクリプト
"""

import os
import sys
import subprocess
import time
import signal
import requests
import webbrowser
from pathlib import Path

def print_status(message, emoji="🔧"):
    """ステータスメッセージを出力"""
    print(f"{emoji} {message}")

def install_dependencies():
    """必要な依存関係をインストール"""
    print_status("依存関係をインストール中...", "📦")
    
    # バックエンド依存関係
    backend_deps = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "google-generativeai==0.3.2",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "pandas==2.1.4",
        "openpyxl==3.1.2"
    ]
    
    for dep in backend_deps:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print_status(f"✅ {dep} インストール完了")
        except subprocess.CalledProcessError:
            print_status(f"⚠️ {dep} は既にインストール済み")

def check_environment():
    """環境変数をチェック"""
    print_status("環境設定をチェック中...", "🔧")
    
    env_file = Path("/.env")
    if not env_file.exists():
        env_example = Path("env.example")
        if env_example.exists():
            print_status("⚠️ .envファイルが見つかりません。env.exampleから作成してください")
            return False
    
    # .envファイルからAPIキーをチェック
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=' not in content or 'your_api_key_here' in content:
                print_status("⚠️ GOOGLE_API_KEYが設定されていません")
                return False
    
    return True

def kill_existing_processes():
    """既存のプロセスを終了"""
    print_status("既存のプロセスをチェック中...", "🔍")
    
    try:
        # ポート8000と3000を使用しているプロセスを終了
        for port in [8000, 3000]:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                     capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            print_status(f"プロセス {pid} (ポート{port}) を終了しました")
                        except ProcessLookupError:
                            pass
            except FileNotFoundError:
                pass
        
        time.sleep(2)
    except Exception as e:
        print_status(f"プロセス終了中にエラー: {e}", "⚠️")

def start_backend():
    """バックエンドサーバーを起動"""
    print_status("バックエンドサーバーを起動中...", "🚀")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_status("❌ backendディレクトリが見つかりません")
        return None
    
    # バックエンドを起動
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # バックエンドの起動を確認
    print_status("バックエンドサーバーの起動を確認中...", "⏳")
    for _ in range(30):  # 30秒待機
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print_status("✅ バックエンドサーバー起動完了", "🎉")
                return backend_process
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        print(".", end="", flush=True)
    
    print_status("❌ バックエンドサーバーが起動しませんでした", "💥")
    return None

def start_frontend():
    """フロントエンドサーバーを起動"""
    print_status("フロントエンドサーバーを起動中...", "🌐")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_status("❌ frontendディレクトリが見つかりません")
        return None
    
    # npm依存関係をインストール
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print_status("✅ npm依存関係インストール完了")
    except subprocess.CalledProcessError:
        print_status("⚠️ npm依存関係のインストールに失敗しました")
    
    # フロントエンドを起動
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # フロントエンドの起動を確認
    print_status("フロントエンドサーバーの起動を確認中...", "⏳")
    for _ in range(60):  # 60秒待機
        try:
            response = requests.get("http://localhost:3000/", timeout=2)
            if response.status_code == 200:
                print_status("✅ フロントエンドサーバー起動完了", "🎉")
                return frontend_process
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        print(".", end="", flush=True)
    
    print_status("❌ フロントエンドサーバーが起動しませんでした", "💥")
    return None

def main():
    """メイン関数"""
    print_status("マーケティングインタビューシステム（改善版）を起動中...", "🚀")
    print("=" * 60)
    
    # プロジェクトルートに移動
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 環境チェック
    if not check_environment():
        print_status("環境設定を確認してください", "❌")
        return
    
    # 依存関係インストール
    install_dependencies()
    
    # 既存プロセス終了
    kill_existing_processes()
    
    # バックエンド起動
    backend_process = start_backend()
    if not backend_process:
        print_status("バックエンドの起動に失敗しました", "❌")
        return
    
    # フロントエンド起動
    frontend_process = start_frontend()
    if not frontend_process:
        print_status("フロントエンドの起動に失敗しました", "❌")
        backend_process.terminate()
        return
    
    # ブラウザを開く
    print_status("ブラウザを開いています...", "🌐")
    webbrowser.open("http://localhost:3000")
    
    print()
    print("=" * 60)
    print_status("🎉 マーケティングインタビューシステムが起動しました！")
    print_status("🌐 アクセス先: http://localhost:3000")
    print_status("📚 API文書: http://localhost:8000/docs")
    print("=" * 60)
    print_status("終了するには Ctrl+C を押してください", "⏹️")
    
    try:
        # プロセスが終了するまで待機
        while True:
            time.sleep(1)
            # プロセスが終了していないかチェック
            if backend_process.poll() is not None:
                print_status("バックエンドプロセスが終了しました", "⚠️")
                break
            if frontend_process.poll() is not None:
                print_status("フロントエンドプロセスが終了しました", "⚠️")
                break
    
    except KeyboardInterrupt:
        print_status("アプリケーションを終了中...", "🛑")
        
        # プロセスを終了
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print_status("アプリケーションが終了しました", "✅")

if __name__ == "__main__":
    main()
