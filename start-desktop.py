#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - シンプルデスクトップ起動
確実に動作する簡単なランチャー
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# アプリケーションディレクトリの設定
APP_DIR = Path(__file__).parent.absolute()
FRONTEND_DIR = APP_DIR / "frontend"
BACKEND_DIR = APP_DIR / "backend"

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
        else:
            # 基本的な.envファイルを作成
            with open(env_file, 'w') as f:
                f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
                f.write("NEXT_PUBLIC_API_URL=http://127.0.0.1:8000\n")
            print("📝 .envファイルを作成しました")
    
    # APIキーの確認
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_google_api_key_here' in content:
            print("⚠️  GOOGLE_API_KEYが設定されていません")
            print(f"   {env_file} を編集してAPIキーを設定してください")
            choice = input("続行しますか？ (y/N): ")
            if choice.lower() != 'y':
                return False
    
    return True

def install_python_deps():
    """Python依存関係をインストール"""
    print("🐍 Python依存関係をチェック中...")
    
    try:
        # 必要なパッケージを個別にチェック・インストール
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
        
        # package.jsonの確認
        if not Path("package.json").exists():
            print("❌ package.jsonが見つかりません")
            return False
        
        # 重要なパッケージの確認
        required_dirs = ["node_modules/electron", "node_modules/next"]
        needs_install = any(not Path(d).exists() for d in required_dirs)
        
        if needs_install:
            print("📦 Node.js依存関係をインストール中...")
            
            # 既存のnode_modulesとpackage-lock.jsonを削除してクリーンインストール
            import shutil
            if Path("node_modules").exists():
                print("🧹 既存のnode_modulesを削除中...")
                shutil.rmtree("node_modules")
            
            if Path("package-lock.json").exists():
                Path("package-lock.json").unlink()
            
            # 依存関係の競合を解決するため --legacy-peer-deps フラグを使用
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
                        env[key] = value
        
        # バックエンドサーバーを起動
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ], env=env)
        
        # バックエンドの起動を確認
        time.sleep(3)
        if backend_process.poll() is None:
            print("✅ バックエンドサーバーが起動しました")
            return backend_process
        else:
            print("❌ バックエンドサーバーの起動に失敗しました")
            return None
            
    except Exception as e:
        print(f"❌ バックエンドサーバーの起動エラー: {e}")
        return None

def start_frontend():
    """フロントエンドを起動"""
    print("🖥️  デスクトップアプリを起動中...")
    
    try:
        os.chdir(FRONTEND_DIR)
        
        # Next.jsサーバーを起動
        print("📱 Next.jsサーバーを起動中...")
        next_process = subprocess.Popen([
            "npm", "run", "dev"
        ])
        
        # Next.jsの起動を待つ
        print("⏳ Next.jsサーバーの起動を待機中...")
        time.sleep(10)
        
        # Electronアプリを起動
        print("🖥️  Electronアプリを起動中...")
        electron_process = subprocess.Popen([
            "npx", "electron", "."
        ])
        
        print("✅ デスクトップアプリが起動しました")
        return next_process, electron_process
        
    except Exception as e:
        print(f"❌ デスクトップアプリの起動エラー: {e}")
        return None, None

def main():
    """メイン関数"""
    print("🎉 マーケティングインタビューシステム デスクトップアプリ")
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
    
    # バックエンド起動
    backend_process = start_backend()
    if not backend_process:
        return 1
    
    # フロントエンド起動
    next_process, electron_process = start_frontend()
    if not next_process or not electron_process:
        if backend_process:
            backend_process.terminate()
        return 1
    
    print("\n✅ アプリケーションが正常に起動しました！")
    print("💡 デスクトップアプリケーションが別ウィンドウで開いています")
    print("🛑 終了するには Ctrl+C を押してください")
    print("-" * 60)
    
    # プロセス監視
    try:
        while True:
            time.sleep(1)
            
            # プロセスの状態チェック
            if backend_process.poll() is not None:
                print("\n❌ バックエンドサーバーが終了しました")
                break
            
            if electron_process.poll() is not None:
                print("\n🏁 デスクトップアプリが終了されました")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 終了要求を受信しました")
    
    finally:
        print("🔄 プロセスを終了中...")
        for process in [electron_process, next_process, backend_process]:
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
