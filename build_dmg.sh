#!/bin/bash
# build_dmg.sh - Pixa DMGビルドスクリプト

echo "🎨 Pixa DMGビルドスクリプト"

# ビルドタイプを選択
echo "ビルドタイプを選択してください:"
echo "1) ライト版 (SD1.5のみ, ~5GB)"
echo "2) スタンダード版 (人気モデル3つ, ~8GB)"
echo "3) プロ版 (全モデル, ~11GB)"
read -p "選択 (1-3): " BUILD_TYPE

# ビルドディレクトリ作成
BUILD_DIR="build/Pixa.app"
mkdir -p "$BUILD_DIR/Contents/MacOS"
mkdir -p "$BUILD_DIR/Contents/Resources"

# PyInstallerでビルド
echo "📦 アプリケーションをビルド中..."
source venv/bin/activate
pyinstaller --name Pixa \
    --windowed \
    --icon=assets/icon.icns \
    --add-data "frontend:frontend" \
    --add-data "backend:backend" \
    --add-data "configs:configs" \
    --hidden-import torch \
    --hidden-import diffusers \
    --collect-all torch \
    --collect-all diffusers \
    pygame_app_improved.py

# モデルをコピー
echo "📥 モデルをコピー中..."
case $BUILD_TYPE in
    1)
        # ライト版: SD1.5のみ
        echo "SD1.5のみを含めます..."
        # 実際のモデルコピー処理
        ;;
    2)
        # スタンダード版
        echo "人気モデル3つを含めます..."
        # 実際のモデルコピー処理
        ;;
    3)
        # プロ版
        echo "全モデルを含めます..."
        cp -r models "$BUILD_DIR/Contents/Resources/"
        ;;
esac

# DMG作成
echo "💿 DMGを作成中..."
DMG_NAME="Pixa-$(date +%Y%m%d).dmg"
create-dmg \
    --volname "Pixa" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --app-drop-link 450 185 \
    "$DMG_NAME" \
    "$BUILD_DIR"

echo "✅ 完了: $DMG_NAME"
echo "📊 サイズ: $(du -h $DMG_NAME | cut -f1)"
