#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tames interview - 超シンプル起動スクリプト
"""

import os
import subprocess
import time
import signal
import requests
from pathlib import Path

def print_status(message, emoji="🔧"):
    """ステータスメッセージを出力"""
    print(f"{emoji} {message}")

def cleanup_ports():
    """ポートをクリーンアップ"""
    print_status("既存のプロセスをクリーンアップ中...", "🧹")
    
    # プロセス名で終了
    patterns = ["uvicorn.*main:app", "npm.*dev", "next.*dev", "next-server"]
    for pattern in patterns:
        try:
            subprocess.run(['pkill', '-f', pattern], capture_output=True)
        except:
            pass
    
    # ポートで終了
    for port in [8000, 3001]:
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        os.kill(int(pid), signal.SIGKILL)
                    except:
                        pass
        except:
            pass
    
    # Next.jsキャッシュクリア
    try:
        subprocess.run(['rm', '-rf', 'frontend/.next'], capture_output=True)
        print_status("Next.jsキャッシュをクリアしました")
    except:
        pass
    
    time.sleep(3)

def main():
    """メイン関数"""
    print_status("tames interview を起動中...", "🚀")
    print("=" * 50)
    
    # プロジェクトルートに移動
    if not Path("backend").exists() or not Path("frontend").exists():
        print_status("❌ backendまたはfrontendディレクトリが見つかりません")
        return
    
    # クリーンアップ
    cleanup_ports()
    
    print_status("バックエンドを起動中...", "🚀")
    
    # バックエンド起動
    backend_process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd="backend"
    )
    
    # バックエンド起動確認
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print_status("✅ バックエンド起動完了", "🎉")
                break
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(".", end="", flush=True)
    else:
        print_status("❌ バックエンドの起動に失敗しました", "💥")
        return
    
    print_status("フロントエンドを起動中...", "🌐")
    
    # npm install
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True, capture_output=True)
        print_status("✅ npm依存関係OK")
    except:
        print_status("⚠️ npm installに失敗しました")
    
    # フロントエンド起動
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev-network-3001"],
        cwd="frontend"
    )
    
    # フロントエンド起動確認（簡単な方法）
    print_status("フロントエンドの起動を確認中...", "⏳")
    for i in range(60):
        try:
            # ポートリスニング確認
            result = subprocess.run(['ss', '-tln'], capture_output=True, text=True)
            if ':3001' in result.stdout:
                print_status("✅ フロントエンド起動完了", "🎉")
                break
        except:
            pass
        time.sleep(2)
        if i % 5 == 0:
            print(".", end="", flush=True)
    else:
        print_status("⚠️ フロントエンドの起動確認がタイムアウトしました", "💥")
        print_status("手動で http://localhost:3001 にアクセスしてください", "🔗")
    
    # 成功メッセージ
    print("\n" + "=" * 60)
    print_status("🎉 tames interview が起動しました！", "🔧")
    print()
    print_status("📱 アクセス先:", "🔧")
    print_status("   http://localhost:3001", "  🔗")
    print_status("   http://10.146.0.2:3001", "  🔗")
    print_status("   http://35.243.121.35:3001", "  🔗")
    print()
    print_status("📚 API文書:", "🔧")
    print_status("   http://localhost:8000/docs", "  📖")
    print("=" * 60)
    print_status("⏹️ 終了するには Ctrl+C を押してください")
    
    # ブラウザを開く
    try:
        import webbrowser
        webbrowser.open("http://localhost:3001")
        print_status("🌐 ブラウザでアプリケーションを開きました")
    except:
        pass
    
    # プロセス監視
    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print_status("⚠️ バックエンドプロセスが終了しました")
                break
            if frontend_process.poll() is not None:
                print_status("⚠️ フロントエンドプロセスが終了しました")
                break
    except KeyboardInterrupt:
        print_status("🛑 アプリケーションを終了中...")
        
        # プロセス終了
        try:
            backend_process.terminate()
            frontend_process.terminate()
            time.sleep(2)
            backend_process.kill()
            frontend_process.kill()
        except:
            pass
        
        print_status("アプリケーションが終了しました", "✅")

if __name__ == "__main__":
    main()
