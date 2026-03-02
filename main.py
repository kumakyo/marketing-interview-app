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

def check_env_file():
    """環境変数ファイルをチェック"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        print_status("⚠️ .envファイルが見つかりません", "⚠️")
        if env_example.exists():
            print_status(".envファイルを作成中...", "📝")
            import shutil
            shutil.copy(env_example, env_file)
            print_status("✅ .envファイルを作成しました")
            print_status("⚠️  .envファイルにGemini APIキーを設定してください！", "⚠️")
            print_status("   編集後、再度このスクリプトを実行してください", "ℹ️")
            return False
    
    # APIキーのチェック
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content or 'GOOGLE_API_KEY=' not in content:
            print_status("⚠️ Gemini APIキーが設定されていません", "⚠️")
            print_status("   .envファイルを開いて、GOOGLE_API_KEYを設定してください", "ℹ️")
            print_status("   例: GOOGLE_API_KEY=AIzaSy...", "ℹ️")
            return False
    
    return True

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
    
    # スクリプトのディレクトリに移動
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 環境変数ファイルのチェック
    if not check_env_file():
        print_status("❌ セットアップが完了していません", "💥")
        return
    
    # プロジェクトルートに移動
    if not Path("backend").exists() or not Path("frontend").exists():
        print_status("❌ backendまたはfrontendディレクトリが見つかりません")
        return
    
    # クリーンアップ
    cleanup_ports()
    
    print_status("バックエンドを起動中...", "🚀")
    
    # 仮想環境のPythonパスを取得（絶対パス）
    project_root = Path.cwd()
    venv_python = project_root / "venv" / "bin" / "python3"
    python_cmd = str(venv_python) if venv_python.exists() else "python3"
    
    # SSL証明書が存在するか確認
    cert_file = project_root / "certs" / "cert.pem"
    key_file = project_root / "certs" / "key.pem"
    
    if cert_file.exists() and key_file.exists():
        print_status("🔐 SSL証明書が見つかりました。HTTPSモードで起動します")
        backend_process = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", 
             "--ssl-keyfile", str(key_file), "--ssl-certfile", str(cert_file), "--reload"],
            cwd="backend"
        )
        api_url = "https://localhost:8000/"
    else:
        print_status("⚠️ SSL証明書が見つかりません。HTTPモードで起動します")
        backend_process = subprocess.Popen(
            [python_cmd, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd="backend"
        )
        api_url = "http://localhost:8000/"
    
    # バックエンド起動確認
    for i in range(30):
        try:
            response = requests.get(api_url, timeout=2, verify=False)
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
    
    # npmがインストールされているか確認
    npm_available = subprocess.run(['which', 'npm'], capture_output=True).returncode == 0
    
    if not npm_available:
        print_status("⚠️ npmがインストールされていません", "⚠️")
        print_status("フロントエンドはスキップされますが、バックエンドは動作しています", "ℹ️")
        frontend_process = None
        frontend_url = None
    else:
        # npm install
        try:
            subprocess.run(["npm", "install"], cwd="frontend", check=True, capture_output=True)
            print_status("✅ npm依存関係OK")
        except:
            print_status("⚠️ npm installに失敗しました")
        
        # SSL証明書が存在する場合はHTTPS、そうでなければHTTP
        if cert_file.exists() and key_file.exists():
            print_status("🔐 フロントエンドをHTTPSモードで起動中...")
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev-https-3001"],
                cwd="frontend"
            )
            frontend_url = "https://localhost:3001"
        else:
            print_status("⚠️ フロントエンドをHTTPモードで起動中...")
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev-network-3001"],
                cwd="frontend"
            )
            frontend_url = "http://localhost:3001"
    
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
        print_status(f"手動で {frontend_url} にアクセスしてください", "🔗")
    
    # 成功メッセージ
    print("\n" + "=" * 60)
    print_status("🎉 tames interview が起動しました！", "🔧")
    print()
    print_status("📱 アクセス先:", "🔧")
    if frontend_process and frontend_url:
        print_status(f"   {frontend_url}", "  🔗")
        if cert_file.exists() and key_file.exists():
            print_status("   ⚠️ 自己署名証明書を使用しています", "  🔒")
            print_status("   ブラウザで警告が表示された場合は「詳細」→「アクセスする」をクリック", "  ℹ️")
    else:
        print_status("   フロントエンドは起動していません（npmが必要）", "  ⚠️")
    
    # ローカルIPアドレスを取得
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip and local_ip != "127.0.0.1" and frontend_process and frontend_url:
            protocol = "https" if cert_file.exists() and key_file.exists() else "http"
            print_status(f"   {protocol}://{local_ip}:3001", "  🔗")
    except:
        pass
    
    print()
    print_status("📚 API文書:", "🔧")
    if cert_file.exists() and key_file.exists():
        print_status("   https://localhost:8000/docs", "  📖")
    else:
        print_status("   http://localhost:8000/docs", "  📖")
    print("=" * 60)
    print_status("⏹️ 終了するには Ctrl+C を押してください")
    
    # ブラウザを開く（フロントエンドがある場合のみ）
    if frontend_process and frontend_url:
        try:
            import webbrowser
            webbrowser.open(frontend_url)
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
            if frontend_process and frontend_process.poll() is not None:
                print_status("⚠️ フロントエンドプロセスが終了しました")
                break
    except KeyboardInterrupt:
        print_status("🛑 アプリケーションを終了中...")
        
        # プロセス終了
        try:
            backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
            time.sleep(2)
            backend_process.kill()
            if frontend_process:
                frontend_process.kill()
        except:
            pass
        
        print_status("アプリケーションが終了しました", "✅")

if __name__ == "__main__":
    main()









