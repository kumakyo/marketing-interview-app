#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - 改善版Webブラウザ起動
起動タイミングを最適化した版
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
from pathlib import Path

# アプリケーションディレクトリの設定
APP_DIR = Path(__file__).parent.absolute()
FRONTEND_DIR = APP_DIR / "frontend"
BACKEND_DIR = APP_DIR / "backend"

def wait_for_backend(max_wait=60):
    """バックエンドサーバーが完全に起動するまで待機"""
    print("⏳ バックエンドサーバーの起動を確認中...")
    
    try:
        import requests
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ バックエンドサーバー接続確認完了")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print(f"\n❌ バックエンドサーバーが{max_wait}秒以内に起動しませんでした")
    return False

def setup_environment():
    """環境をセットアップ"""
    print("🔧 環境をセットアップ中...")
    
    # .envファイルの確認と作成
    env_file = APP_DIR / ".env"
    if not env_file.exists():
        example_file = APP_DIR / "env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("📝 .envファイルを作成しました")
    
    return True

def install_python_deps():
    """Python依存関係をインストール"""
    print("🐍 Python依存関係をチェック中...")
    
    try:
        required_packages = ['fastapi', 'uvicorn', 'google-generativeai', 'python-dotenv']
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                print(f"📦 {package}をインストール中...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], check=True)
        
        print("✅ Python依存関係OK")
        return True
    except Exception as e:
        print(f"❌ Python依存関係のインストールエラー: {e}")
        return False

def install_node_deps():
    """Node.js依存関係をインストール"""
    print("📦 Node.js依存関係をチェック中...")
    
    try:
        os.chdir(FRONTEND_DIR)
        
        if not Path("package.json").exists():
            print("❌ package.jsonが見つかりません")
            return False
        
        required_dirs = ["node_modules/next"]
        needs_install = any(not Path(d).exists() for d in required_dirs)
        
        if needs_install:
            print("📦 Node.js依存関係をインストール中...")
            
            import shutil
            paths_to_remove = ["node_modules", "package-lock.json", ".next", "out"]
            
            for path in paths_to_remove:
                if Path(path).exists():
                    if Path(path).is_dir():
                        print(f"🧹 {path}/ を削除中...")
                        shutil.rmtree(path)
                    else:
                        print(f"🧹 {path} を削除中...")
                        Path(path).unlink()
            
            subprocess.run(["npm", "cache", "clean", "--force"], check=True)
            subprocess.run(["npm", "install", "--legacy-peer-deps"], check=True)
        
        print("✅ Node.js依存関係OK")
        return True
    except Exception as e:
        print(f"❌ Node.js依存関係のインストールエラー: {e}")
        return False

def start_backend():
    """バックエンドを起動"""
    print("🚀 バックエンドサーバーを起動中...")
    
    try:
        os.chdir(BACKEND_DIR)
        
        # 環境変数を設定
        env = os.environ.copy()
        env_file = APP_DIR / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        env[key] = value.strip().strip('"\'')
        
        # バックエンドサーバーを起動
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "localhost", "--port", "8000", "--reload"
        ], env=env)
        
        # バックエンドの起動を確実に待つ
        if wait_for_backend():
            print("✅ バックエンドサーバーが起動しました (http://localhost:8000)")
            return backend_process
        else:
            print("❌ バックエンドサーバーの起動に失敗しました")
            if backend_process.poll() is None:
                backend_process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ バックエンドサーバーの起動エラー: {e}")
        return None

def start_frontend():
    """フロントエンド（Next.js）を起動"""
    print("🌐 Webアプリケーションを起動中...")
    
    try:
        os.chdir(FRONTEND_DIR)
        
        # 環境変数を設定（バックエンドが起動済みなので確実にURLを設定）
        env = {
            **os.environ, 
            "NEXT_PUBLIC_API_URL": "http://localhost:8000",
            "PORT": "3000"
        }
        
        print("📱 Next.jsサーバーを起動中...")
        next_process = subprocess.Popen([
            "npm", "run", "dev-local"
        ], env=env)
        
        # Next.jsの起動を待つ（バックエンドが既に起動済み）
        print("⏳ Next.jsサーバーの起動を待機中...")
        time.sleep(8)
        
        # ブラウザでアプリケーションを開く
        frontend_url = "http://localhost:3000"
        print("🌐 ブラウザでアプリケーションを開いています...")
        try:
            webbrowser.open(frontend_url)
            print("✅ ブラウザでアプリケーションが開きました")
        except Exception as e:
            print(f"⚠️  ブラウザの自動起動に失敗しました: {e}")
            print(f"   手動で {frontend_url} を開いてください")
        
        return next_process
        
    except Exception as e:
        print(f"❌ Webアプリケーションの起動エラー: {e}")
        return None

def main():
    """メイン関数"""
    print("🌐 マーケティングインタビューシステム Webアプリ（改善版）")
    print("=" * 60)
    
    # 環境セットアップ
    if not setup_environment():
        return 1
    
    # Python依存関係
    if not install_python_deps():
        return 1
    
    # Node.js依存関係
    if not install_node_deps():
        return 1
    
    # バックエンド起動（完全起動まで待機）
    backend_process = start_backend()
    if not backend_process:
        return 1
    
    # フロントエンド起動（バックエンド起動後）
    next_process = start_frontend()
    if not next_process:
        if backend_process:
            backend_process.terminate()
        return 1
    
    print("\n✅ アプリケーションが正常に起動しました！")
    print("🌐 ブラウザでアプリケーションが開いています")
    print("📍 URL: http://localhost:3000")
    print("🔗 API: http://localhost:8000")
    print("🛑 終了するには Ctrl+C を押してください")
    print("-" * 60)
    
    # プロセス監視
    try:
        while True:
            time.sleep(1)
            
            if backend_process.poll() is not None:
                print("\n❌ バックエンドサーバーが終了しました")
                break
            
            if next_process.poll() is not None:
                print("\n🏁 Webアプリケーションが終了されました")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 終了要求を受信しました")
    
    finally:
        print("🔄 プロセスを終了中...")
        for process in [next_process, backend_process]:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("✅ 終了処理完了")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())