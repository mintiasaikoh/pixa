#!/bin/bash
# SDXLモデル対応後の再起動手順

echo "Pixa - SDXLモデル対応版の起動"
echo "================================"

# 既存のサーバーを停止
echo "既存のサーバーを停止中..."
./stop_server.sh

# 少し待機
sleep 2

# 新しいサーバーを起動
echo "SDXLモデル対応版サーバーを起動中..."
./start_server.sh

echo ""
echo "✨ 新機能："
echo "- Pixel Art XL LoRA (nerijs/pixel-art-xl) - 8ステップで高速生成"
echo "- Pixel Party XL (pixelparty/pixel-party-xl) - インディーゲーム向け"
echo "- 1024x1024の高解像度生成に対応"
echo ""
echo "🎮 ブラウザで http://localhost:5001 を開いてください"
