# .envファイルを作成するスクリプト
import shutil
from pathlib import Path

# プロジェクトディレクトリ
project_dir = Path("/home/kyosuke/marketing-interview-app")

# env.exampleから.envを作成
env_example = project_dir / "env.example"
env_file = project_dir / ".env"

if env_example.exists():
    shutil.copy(env_example, env_file)
    print("✅ .envファイルを作成しました")
    print(f"📍 場所: {env_file}")
else:
    print("❌ env.exampleファイルが見つかりません")