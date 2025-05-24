#!/bin/bash
# 不足しているモデルのみダウンロード

cd /Users/mymac/pixa
source venv/bin/activate

echo "🎨 不足しているモデルのみダウンロードします"
echo ""

# 1. pixel-art-style.ckptのみ
echo "📥 pixel-art-style.ckpt (4.1GB)..."
mkdir -p ./models/pixel-art-style
huggingface-cli download kohbanye/pixel-art-style pixel-art-style.ckpt --local-dir ./models/pixel-art-style --resume-download

# 2. Sprite Sheet Generator（必要なら）
echo "📥 Sprite Sheet Generator（オプション）..."
echo "必要な場合は以下を実行："
echo "huggingface-cli download Onodofthenorth/SD_PixelArt_SpriteSheet_Generator"

echo ""
echo "✅ 完了！"
