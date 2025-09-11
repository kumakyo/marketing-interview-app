#!/bin/bash
# Electronに必要なシステムライブラリをインストールするスクリプト

echo "🔧 Electronに必要なシステムライブラリをインストール中..."

# ATK（Accessibility Toolkit）とその他のElectron依存ライブラリをインストール
sudo apt-get update

sudo apt-get install -y \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0

echo "✅ Electronライブラリのインストール完了"
