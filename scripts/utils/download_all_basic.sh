#!/bin/bash
# 全モデルを確実にダウンロード

cd /Users/mymac/pixa
source venv/bin/activate

echo "🎨 Pixaの全モデルをダウンロードします"
echo ""

# 1. SD1.5
echo "📥 [1/5] Stable Diffusion v1.5..."
huggingface-cli download runwayml/stable-diffusion-v1-5 --resume-download

# 2. All-In-One
echo "📥 [2/5] All-In-One Pixel Model..."
huggingface-cli download PublicPrompts/All-In-One-Pixel-Model --resume-download

# 3. pixel-art-style
echo "📥 [3/5] pixel-art-style (.ckpt)..."
mkdir -p ./models/pixel-art-style
huggingface-cli download kohbanye/pixel-art-style pixel-art-style.ckpt --local-dir ./models/pixel-art-style --resume-download

# 4. Sprite Sheet Generator
echo "📥 [4/5] Sprite Sheet Generator..."
huggingface-cli download Onodofthenorth/SD_PixelArt_SpriteSheet_Generator --resume-download

# 5. Analog Diffusion
echo "📥 [5/5] Analog Diffusion..."
huggingface-cli download wavymulder/Analog-Diffusion --resume-download

echo ""
echo "✅ 基本モデルのダウンロード完了！"
echo "🚀 サーバーを再起動してください"
