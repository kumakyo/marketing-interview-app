#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - シンプル起動スクリプト
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

def cleanup_ports():
    """ポートを使用しているプロセスをクリーンアップ"""
    print_status("既存のプロセスをクリーンアップ中...", "🧹")
    
    for port in [8000, 3001]:
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                 capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print_status(f"ポート{port}のプロセス {pid} を終了しました")
                        time.sleep(1)
                        # 強制終了が必要な場合
                        try:
                            os.kill(int(pid), 0)  # プロセス存在チェック
                            os.kill(int(pid), signal.SIGKILL)
                            print_status(f"プロセス {pid} を強制終了しました")
                        except ProcessLookupError:
                            pass
                    except (ValueError, ProcessLookupError):
                        pass
        except subprocess.SubprocessError:
            pass
    
    # Next.jsキャッシュをクリア
    try:
        next_cache = Path("frontend/.next")
        if next_cache.exists():
            subprocess.run(['rm', '-rf', str(next_cache)], capture_output=True)
            print_status("Next.jsキャッシュをクリアしました")
    except:
        pass
    
    time.sleep(2)

def start_backend():
    """バックエンドを起動"""
    print_status("バックエンドサーバーを起動中...", "🚀")
    
    backend_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 起動確認
    print_status("バックエンドの起動を確認中...", "⏳")
    for _ in range(30):
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
    """フロントエンドを起動"""
    print_status("フロントエンドサーバーを起動中...", "🌐")
    
    # npm install
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True, 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_status("✅ npm依存関係インストール完了")
    except subprocess.CalledProcessError:
        print_status("⚠️ npm依存関係のインストールに失敗しました")
    
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev-network-3001"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 起動確認
    print_status("フロントエンドの起動を確認中...", "⏳")
    for _ in range(60):
        try:
            if frontend_process.poll() is not None:
                print_status("❌ フロントエンドプロセスが終了しました", "💥")
                return None
            
            response = requests.get("http://localhost:3001/", timeout=2)
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
    print_status("マーケティングインタビューシステム（シンプル版）を起動中...", "🚀")
    print("=" * 60)
    
    # プロジェクトルートに移動
    if not Path("backend").exists() or not Path("frontend").exists():
        print_status("❌ backendまたはfrontendディレクトリが見つかりません")
        print_status("marketing-interview-appディレクトリ内で実行してください")
        return
    
    # 既存プロセスのクリーンアップ
    cleanup_ports()
    
    # バックエンド起動
    backend_process = start_backend()
    if not backend_process:
        print_status("バックエンドの起動に失敗しました", "❌")
        return
    
    # フロントエンド起動
    frontend_process = start_frontend()
    if not frontend_process:
        print_status("フロントエンドの起動に失敗しました", "❌")
        if backend_process:
            backend_process.terminate()
        return
    
    # 成功メッセージ
    print("\n" + "=" * 70)
    print_status("🎉 マーケティングインタビューシステムが起動しました！", "🔧")
    print()
    print_status("📱 ローカルアクセス:", "🔧")
    print_status("   http://localhost:3001", "  🔗")
    print()
    print_status("🌐 ネットワークアクセス（他のデバイスから）:", "🔧")
    print_status("   http://10.146.0.2:3001", "  🔗")
    print_status("   http://35.243.121.35:3001", "  🔗")
    print()
    print_status("📚 API文書:", "🔧")
    print_status("   http://localhost:8000/docs", "  📖")
    print_status("   http://10.146.0.2:8000/docs", "  📖")
    print()
    print_status("🔒 セキュリティ設定: 全IPアドレスからのアクセスを許可", "🔧")
    print("=" * 70)
    print_status("⏹️ 終了するには Ctrl+C を押してください")
    
    # ブラウザを開く
    try:
        webbrowser.open("http://localhost:3001")
        print_status("🌐 ブラウザでアプリケーションを開きました")
    except:
        pass
    
    # プロセス監視
    try:
        while True:
            time.sleep(1)
            
            # プロセスが終了していないかチェック
            if backend_process.poll() is not None:
                print_status("⚠️ バックエンドプロセスが終了しました")
                break
            if frontend_process.poll() is not None:
                print_status("⚠️ フロントエンドプロセスが終了しました")
                break
                
    except KeyboardInterrupt:
        print_status("🛑 アプリケーションを終了中...")
        
        # プロセス終了
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print_status("アプリケーションが終了しました", "✅")

if __name__ == "__main__":
    main()



