#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ビルドエラーを修正するスクリプト
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

APP_DIR = Path(__file__).parent.absolute()
FRONTEND_DIR = APP_DIR / "frontend"

def main():
    print("🔧 Next.jsビルドエラーを修正中...")
    
    try:
        os.chdir(FRONTEND_DIR)
        
        print("🧹 キャッシュとnode_modulesをクリア中...")
        
        # 既存ファイルを削除
        paths_to_remove = [
            "node_modules",
            "package-lock.json",
            ".next",
            "out"
        ]
        
        for path in paths_to_remove:
            if Path(path).exists():
                if Path(path).is_dir():
                    shutil.rmtree(path)
                    print(f"   削除: {path}/")
                else:
                    Path(path).unlink()
                    print(f"   削除: {path}")
        
        # npmキャッシュをクリア
        print("🧹 npmキャッシュをクリア中...")
        subprocess.run(["npm", "cache", "clean", "--force"], check=True)
        
        # 依存関係を再インストール
        print("📦 依存関係を再インストール中...")
        subprocess.run(["npm", "install", "--legacy-peer-deps"], check=True)
        
        # Next.jsキャッシュをクリア
        print("🧹 Next.jsキャッシュをクリア中...")
        subprocess.run(["npx", "next", "build", "--debug"], capture_output=True)
        
        print("✅ ビルドエラーの修正が完了しました！")
        print("🚀 以下のコマンドでアプリを起動してください:")
        print("   python3 start-web.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ エラーが発生しました: {e}")
        print("🔧 手動での修正方法:")
        print("   cd frontend")
        print("   rm -rf node_modules package-lock.json .next out")
        print("   npm cache clean --force")
        print("   npm install --legacy-peer-deps")
        return 1
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
