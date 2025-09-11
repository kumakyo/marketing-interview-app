#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依存関係の問題を修正するクイックフィックススクリプト
"""

import os
import subprocess
import shutil
from pathlib import Path

APP_DIR = Path(__file__).parent.absolute()
FRONTEND_DIR = APP_DIR / "frontend"

def main():
    print("🔧 依存関係の問題を修正中...")
    
    try:
        os.chdir(FRONTEND_DIR)
        
        # node_modulesとpackage-lock.jsonを削除
        print("🧹 既存ファイルをクリーンアップ中...")
        if Path("node_modules").exists():
            shutil.rmtree("node_modules")
            
        if Path("package-lock.json").exists():
            Path("package-lock.json").unlink()
            
        # npmキャッシュをクリア
        print("🧹 npmキャッシュをクリア中...")
        subprocess.run(["npm", "cache", "clean", "--force"], check=True)
        
        # 依存関係を再インストール
        print("📦 依存関係を再インストール中...")
        subprocess.run(["npm", "install", "--legacy-peer-deps", "--no-audit"], check=True)
        
        print("✅ 依存関係の修正が完了しました！")
        print("🚀 今度は以下のコマンドでアプリを起動してください:")
        print("   python3 start-desktop.py")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("🔧 手動での修正方法:")
        print("   cd frontend")
        print("   rm -rf node_modules package-lock.json")
        print("   npm install --legacy-peer-deps")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
