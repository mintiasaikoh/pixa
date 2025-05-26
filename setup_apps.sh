#!/bin/bash

# Pixa.app作成準備スクリプト
# すべてのapp作成スクリプトに実行権限を付与

echo "🔧 Pixa.app作成スクリプトの準備中..."

# 実行権限を付与
chmod +x create_app.sh
chmod +x create_app_pro.sh
chmod +x create_app_desktop.sh

echo "✅ 準備完了！"
echo ""
echo "📱 利用可能なオプション:"
echo ""
echo "1. シンプル版（ターミナル表示あり）"
echo "   ./create_app.sh"
echo ""
echo "2. プロ版（バックグラウンド動作）"
echo "   ./create_app_pro.sh"
echo ""
echo "3. デスクトップ版（Pygame）"
echo "   ./create_app_desktop.sh"
echo ""
echo "詳細は APP_GUIDE.md を参照してください。"