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
import socket
from pathlib import Path

def print_status(message, emoji="🔧"):
    """ステータスメッセージを出力"""
    print(f"{emoji} {message}")

def get_local_ip():
    """ローカルIPアドレスを取得"""
    try:
        # ダミーのUDP接続を作成してローカルIPを取得
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

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
    
    env_file = Path(".env")
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
        # まず特定のプロセス名で検索して終了（自分自身は除外）
        current_pid = os.getpid()
        process_patterns = [
            "uvicorn.*main:app", 
            "npm.*dev-network-3001",
            "next.*dev",
            "next-server"
        ]
        
        for pattern in process_patterns:
            try:
                # プロセス一覧を取得して自分自身を除外
                result = subprocess.run(['pgrep', '-f', pattern], 
                                     capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            pid_int = int(pid)
                            if pid_int != current_pid:  # 自分自身は除外
                                os.kill(pid_int, signal.SIGTERM)
                                print_status(f"プロセス {pid} ({pattern}) を終了しました")
                        except (ValueError, ProcessLookupError):
                            pass
            except subprocess.SubprocessError:
                pass
        
        # 少し待機
        time.sleep(2)
        
        # ポート8000と3000、3001を使用しているプロセスを終了
        for port in [8000, 3000, 3001]:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                     capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            # まずSIGTERMで終了を試行
                            os.kill(int(pid), signal.SIGTERM)
                            print_status(f"プロセス {pid} (ポート{port}) を終了しました")
                            time.sleep(1)
                            
                            # まだ生きているかチェック
                            try:
                                os.kill(int(pid), 0)  # プロセス存在チェック
                                # まだ生きている場合は強制終了
                                os.kill(int(pid), signal.SIGKILL)
                                print_status(f"プロセス {pid} を強制終了しました")
                            except ProcessLookupError:
                                # 既に終了済み
                                pass
                                
                        except ProcessLookupError:
                            pass
            except FileNotFoundError:
                pass
        
        # Next.jsキャッシュをクリア
        try:
            frontend_dir = Path("frontend")
            if frontend_dir.exists():
                next_cache = frontend_dir / ".next"
                node_cache = frontend_dir / "node_modules" / ".cache"
                
                if next_cache.exists():
                    subprocess.run(['rm', '-rf', str(next_cache)], 
                                 capture_output=True)
                    print_status("Next.jsキャッシュをクリアしました")
                    
                if node_cache.exists():
                    subprocess.run(['rm', '-rf', str(node_cache)], 
                                 capture_output=True)
        except Exception:
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
    
    # フロントエンドを起動（ポート3001でネットワークアクセス対応）
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev-network-3001"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # フロントエンドの起動を確認
    print_status("フロントエンドサーバーの起動を確認中...", "⏳")
    for i in range(60):  # 60秒待機
        try:
            # プロセスが生きているかチェック
            if frontend_process.poll() is not None:
                # プロセスが終了している場合、エラー出力を表示
                stdout, stderr = frontend_process.communicate()
                print_status(f"❌ フロントエンドプロセスが終了しました", "💥")
                if stderr:
                    print_status(f"エラー: {stderr.decode()[:200]}", "⚠️")
                return None
            
            response = requests.get("http://localhost:3001/", timeout=2)
            if response.status_code == 200:
                print_status("✅ フロントエンドサーバー起動完了", "🎉")
                return frontend_process
        except requests.exceptions.RequestException:
            pass
        
        # 10秒ごとにポート状況をチェック
        if i % 10 == 0 and i > 0:
            try:
                result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
                if ':3001' in result.stdout:
                    print_status("ポート3001は使用中です", "🔍")
                else:
                    print_status("ポート3001は空いています", "🔍")
            except:
                pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print_status("❌ フロントエンドサーバーが起動しませんでした", "💥")
    
    # プロセスが生きている場合、エラー出力を確認
    if frontend_process.poll() is None:
        frontend_process.terminate()
        try:
            stdout, stderr = frontend_process.communicate(timeout=5)
            if stderr:
                print_status(f"エラー出力: {stderr.decode()[:300]}", "⚠️")
        except:
            pass
    
    return None

def main():
    """メイン関数"""
    print_status("マーケティングインタビューシステム（改善版）を起動中...", "🚀")
    print("=" * 60)
    
    # プロジェクトルートに移動
    current_dir = Path.cwd()
    if current_dir.name != "marketing-interview-app":
        # marketing-interview-appディレクトリを探す
        if (current_dir / "marketing-interview-app").exists():
            os.chdir(current_dir / "marketing-interview-app")
        elif current_dir.parent.name == "marketing-interview-app":
            os.chdir(current_dir.parent)
        # 既にmarketing-interview-appディレクトリ内にいる場合はそのまま
    
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
    webbrowser.open("http://localhost:3001")
    
    # IPアドレス情報を取得
    local_ip = get_local_ip()
    
    print()
    print("=" * 70)
    print_status("🎉 マーケティングインタビューシステムが起動しました！")
    print()
    print_status("📱 ローカルアクセス:")
    print_status("   http://localhost:3001", "  🔗")
    print()
    print_status("🌐 ネットワークアクセス（他のデバイスから）:")
    print_status(f"   http://{local_ip}:3001", "  🔗")
    print()
    print_status("📚 API文書:")
    print_status("   http://localhost:8000/docs", "  📖")
    print_status(f"   http://{local_ip}:8000/docs", "  📖")
    print()
    print_status("🔒 セキュリティ設定: 全IPアドレスからのアクセスを許可")
    print("=" * 70)
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


