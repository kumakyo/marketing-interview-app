#!/bin/bash

# 実行権限を付与
chmod +x /home/kyosuke/marketing-interview-app/install-electron-deps.sh
chmod +x /home/kyosuke/marketing-interview-app/start-web.py
chmod +x /home/kyosuke/marketing-interview-app/check-system.py

# システムチェックを実行
python3 /home/kyosuke/marketing-interview-app/check-system.py
