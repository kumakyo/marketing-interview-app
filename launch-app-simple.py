#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マーケティングインタビューシステム - シンプルランチャー
ダブルクリックで起動できるPythonランチャー
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# アプリケーションディレクトリの設定
APP_DIR = Path(__file__).parent.absolute()
FRONTEND_DIR = APP_DIR / "frontend"
BACKEND_DIR = APP_DIR / "backend"

class MarketingInterviewLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True

    def check_requirements(self):
        """必要な環境をチェック"""
        print("🔍 システム要件をチェック中...")
        
        # .envファイルの確認
        env_file = APP_DIR / ".env"
        if not env_file.exists():
            print("❌ .envファイルが見つかりません。")
            print(f"📝 {APP_DIR}/env.example を {APP_DIR}/.env にコピーして、")
            print("   GOOGLE_API_KEYを設定してください。")
            
            # 自動的に.envファイルを作成
            example_file = APP_DIR / "env.example"
            if example_file.exists():
                import shutil
                shutil.copy(example_file, env_file)
                print("✅ .envファイルを自動作成しました。APIキーを設定してください。")
            
            return False

        # Python依存関係の確認
        requirements_file = BACKEND_DIR / "requirements.txt"
        if not requirements_file.exists():
            print("❌ バックエンドの要件ファイルが見つかりません。")
            return False

        # Node.js依存関係の確認
        package_json = FRONTEND_DIR / "package.json"
        if not package_json.exists():
            print("❌ フロントエンドの設定ファイルが見つかりません。")
            return False

        print("✅ システム要件チェック完了")
        return True

    def install_dependencies(self):
        """依存関係をインストール"""
        print("📦 依存関係をインストール中...")
        
        # Python依存関係
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-q", "-r", 
                str(BACKEND_DIR / "requirements.txt")
            ], check=True, cwd=BACKEND_DIR)
            print("✅ Python依存関係のインストール完了")
        except subprocess.CalledProcessError:
            print("❌ Python依存関係のインストールに失敗しました")
            return False

        # Node.js依存関係
        try:
            print("📦 Node.js依存関係をインストール中...")
            # package.jsonがあることを確認
            if not (FRONTEND_DIR / "package.json").exists():
                print("❌ package.jsonが見つかりません")
                return False
            
            # node_modulesが存在しない場合、または不完全な場合は再インストール
            if not (FRONTEND_DIR / "node_modules").exists() or not (FRONTEND_DIR / "node_modules" / "concurrently").exists():
                # 既存のnode_modulesがあれば削除
                import shutil
                if (FRONTEND_DIR / "node_modules").exists():
                    shutil.rmtree(FRONTEND_DIR / "node_modules")
                
                subprocess.run(["npm", "install", "--legacy-peer-deps"], check=True, cwd=FRONTEND_DIR)
            
            # 重要なパッケージが確実にインストールされているかチェック
            required_packages = ["concurrently", "wait-on", "electron"]
            for package in required_packages:
                if not (FRONTEND_DIR / "node_modules" / package).exists():
                    print(f"📦 {package}を個別にインストール中...")
                    subprocess.run(["npm", "install", package, "--legacy-peer-deps"], check=True, cwd=FRONTEND_DIR)
            
            print("✅ Node.js依存関係のインストール完了")
        except subprocess.CalledProcessError as e:
            print(f"❌ Node.js依存関係のインストールに失敗しました: {e}")
            return False

        return True

    def start_backend(self):
        """バックエンドサーバーを起動"""
        print("🚀 バックエンドサーバーを起動中...")
        
        env = os.environ.copy()
        # .envファイルの内容を環境変数に読み込み
        env_file = APP_DIR / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value

        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "127.0.0.1", "--port", "8000"
            ], cwd=BACKEND_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # バックエンドの起動を少し待つ
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ バックエンドサーバーが起動しました (http://127.0.0.1:8000)")
                return True
            else:
                print("❌ バックエンドサーバーの起動に失敗しました")
                return False
                
        except Exception as e:
            print(f"❌ バックエンドサーバーの起動エラー: {e}")
            return False

    def start_frontend(self):
        """フロントエンド（Electron）を起動"""
        print("🖥️  デスクトップアプリケーションを起動中...")
        
        try:
            # まずNext.jsサーバーを起動
            print("📱 フロントエンドサーバーを起動中...")
            next_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=FRONTEND_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Next.jsサーバーの起動を待つ
            import time
            time.sleep(8)
            
            # Electronアプリを起動
            print("🖥️  Electronアプリを起動中...")
            self.frontend_process = subprocess.Popen([
                "npx", "electron", "."
            ], cwd=FRONTEND_DIR)
            
            print("✅ デスクトップアプリケーションが起動しました")
            return True
            
        except Exception as e:
            print(f"❌ デスクトップアプリケーションの起動エラー: {e}")
            return False

    def cleanup(self):
        """プロセスをクリーンアップ"""
        print("\n🛑 アプリケーションを終了しています...")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        print("✅ 終了処理完了")

    def signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        self.running = False
        self.cleanup()
        sys.exit(0)

    def run(self):
        """メインの実行関数"""
        print("🎉 マーケティングインタビューシステム デスクトップアプリ")
        print("=" * 60)
        
        # シグナルハンドラーを設定
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # 要件チェック
            if not self.check_requirements():
                input("Enterキーを押して終了...")
                return False
            
            # 依存関係インストール
            if not self.install_dependencies():
                input("Enterキーを押して終了...")
                return False
            
            # バックエンド起動
            if not self.start_backend():
                input("Enterキーを押して終了...")
                return False
            
            # フロントエンド起動
            if not self.start_frontend():
                self.cleanup()
                input("Enterキーを押して終了...")
                return False
            
            print("\n✅ アプリケーションが正常に起動しました！")
            print("💡 アプリケーションウィンドウが別途開いています")
            print("🛑 終了するには Ctrl+C を押してください")
            print("-" * 60)
            
            # プロセスの監視
            while self.running:
                time.sleep(1)
                
                # バックエンドプロセスのチェック
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ バックエンドサーバーが予期せず終了しました")
                    break
                
                # フロントエンドプロセスのチェック
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("🏁 アプリケーションが終了されました")
                    break
            
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

def main():
    """メイン関数"""
    launcher = MarketingInterviewLauncher()
    success = launcher.run()
    
    if not success:
        input("何かキーを押してください...")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
