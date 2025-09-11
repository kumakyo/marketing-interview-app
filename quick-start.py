#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クイックスタート - 最初に実行するスクリプト
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 マーケティングインタビューシステム クイックスタート")
    print("=" * 60)
    
    app_dir = Path(__file__).parent.absolute()
    os.chdir(app_dir)
    
    # 1. システムチェック
    print("📋 ステップ1: システム環境チェック")
    try:
        result = subprocess.run([sys.executable, "check-system.py"], check=True)
        print("✅ システムチェック完了")
    except subprocess.CalledProcessError:
        print("⚠️  システムチェックで問題が検出されました")
        print("   上記の指示に従って修正してください")
        return 1
    
    # 2. 環境設定確認
    print("\n📋 ステップ2: 環境設定確認")
    env_file = app_dir / ".env"
    if not env_file.exists():
        print("📝 .envファイルを作成中...")
        example_file = app_dir / "env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ .envファイルを作成しました")
        else:
            with open(env_file, 'w') as f:
                f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
                f.write("NEXT_PUBLIC_API_URL=http://localhost:8000\n")
            print("✅ .envファイルを作成しました")
    
    # APIキーの確認
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_google_api_key_here' in content:
            print("⚠️  GOOGLE_API_KEYが設定されていません")
            print(f"   {env_file} を編集してAPIキーを設定してください")
            print("   Google AI Studio: https://makersuite.google.com/app/apikey")
    
    # 3. 動作テスト
    print("\n📋 ステップ3: 動作テスト（オプション）")
    choice = input("動作テストを実行しますか？ (y/N): ")
    if choice.lower() == 'y':
        try:
            subprocess.run([sys.executable, "test-app.py"], check=True)
        except subprocess.CalledProcessError:
            print("⚠️  動作テストで問題が検出されました")
    
    # 4. 起動方法の案内
    print("\n" + "=" * 60)
    print("🎉 セットアップ完了！")
    print("\n💡 アプリケーションの起動方法:")
    print("   🌐 Webアプリ（推奨）: python3 start-web.py")
    print("   🖥️  デスクトップアプリ: python3 start-desktop.py")
    print("\n📚 その他のコマンド:")
    print("   🔧 システムチェック: python3 check-system.py")
    print("   🧪 動作テスト: python3 test-app.py")
    print("   🔄 依存関係修正: python3 fix-dependencies.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
