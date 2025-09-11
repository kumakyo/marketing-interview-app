#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
システム環境チェックツール
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python():
    """Python環境をチェック"""
    print("🐍 Python環境チェック:")
    print(f"   Python バージョン: {sys.version}")
    
    # 必要なパッケージをチェック
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'google.generativeai': 'Google Generative AI',
        'dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (未インストール)")
            missing_packages.append(name)
    
    return len(missing_packages) == 0

def check_node():
    """Node.js環境をチェック"""
    print("\n📦 Node.js環境チェック:")
    
    # Node.jsバージョンチェック
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
        print(f"   Node.js バージョン: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ Node.js が見つかりません")
        return False
    
    # npmバージョンチェック
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, check=True)
        print(f"   npm バージョン: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ npm が見つかりません")
        return False
    
    return True

def check_electron_deps():
    """Electron依存関係をチェック"""
    print("\n🖥️  Electron依存関係チェック:")
    
    # 必要なライブラリのチェック
    required_libs = [
        'libatk-1.0.so.0',
        'libgtk-3.so.0',
        'libgdk-pixbuf-2.0.so.0'
    ]
    
    missing_libs = []
    for lib in required_libs:
        try:
            result = subprocess.run(['ldconfig', '-p'], capture_output=True, text=True)
            if lib in result.stdout:
                print(f"   ✅ {lib}")
            else:
                print(f"   ❌ {lib} (未インストール)")
                missing_libs.append(lib)
        except Exception:
            print(f"   ❓ {lib} (チェック不可)")
    
    return len(missing_libs) == 0

def check_environment():
    """環境変数をチェック"""
    print("\n🔧 環境設定チェック:")
    
    app_dir = Path(__file__).parent.absolute()
    env_file = app_dir / ".env"
    
    if env_file.exists():
        print("   ✅ .envファイル存在")
        
        # APIキーの確認
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=' in content and 'your_google_api_key_here' not in content:
                print("   ✅ GOOGLE_API_KEY設定済み")
            else:
                print("   ⚠️  GOOGLE_API_KEYが未設定")
                return False
    else:
        print("   ❌ .envファイルなし")
        return False
    
    return True

def check_display():
    """ディスプレイ環境をチェック"""
    print("\n🖼️  ディスプレイ環境チェック:")
    
    if 'DISPLAY' in os.environ:
        print(f"   ✅ DISPLAY環境変数: {os.environ['DISPLAY']}")
    else:
        print("   ❌ DISPLAY環境変数なし (Electronが動作しない可能性)")
    
    if 'WAYLAND_DISPLAY' in os.environ:
        print(f"   ✅ WAYLAND_DISPLAY: {os.environ['WAYLAND_DISPLAY']}")
    
    # X11サーバーの確認
    try:
        subprocess.run(['xset', 'q'], capture_output=True, check=True)
        print("   ✅ X11サーバー動作中")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ X11サーバー未動作")
        return False

def main():
    """メイン関数"""
    print("🔍 マーケティングインタビューシステム 環境チェック")
    print("=" * 60)
    
    checks = [
        ("Python環境", check_python),
        ("Node.js環境", check_node),
        ("Electron依存関係", check_electron_deps),
        ("環境設定", check_environment),
        ("ディスプレイ環境", check_display)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name}チェック中にエラー: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 チェック結果サマリー:")
    
    all_ok = True
    for name, result in results:
        status = "✅ OK" if result else "❌ NG"
        print(f"   {status} {name}")
        if not result:
            all_ok = False
    
    print("\n💡 推奨起動方法:")
    if all_ok:
        print("   🖥️  デスクトップアプリ: python3 start-desktop.py")
        print("   🌐 Webアプリ: python3 start-web.py")
    elif not results[2][1] or not results[4][1]:  # Electron依存関係またはディスプレイ環境がNG
        print("   🌐 Webアプリ（推奨）: python3 start-web.py")
        print("   🔧 Electron修正: chmod +x install-electron-deps.sh && ./install-electron-deps.sh")
    else:
        print("   🔧 環境を修正してから再実行してください")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
