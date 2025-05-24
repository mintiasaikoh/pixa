#!/bin/bash
# 必須モデルを確実にダウンロードするスクリプト

echo "🎨 Pixa - 必須モデルダウンロード"
echo ""

# venvをアクティベート
source venv/bin/activate

# huggingface-hubがインストールされているか確認
pip install -q huggingface-hub

echo "📥 Stable Diffusion v1.5 をダウンロード中（約4GB）..."
python -c "
from huggingface_hub import snapshot_download
import os

cache_dir = os.path.expanduser('~/.cache/huggingface')
print('キャッシュディレクトリ:', cache_dir)

try:
    snapshot_download(
        'runwayml/stable-diffusion-v1-5',
        cache_dir=cache_dir,
        resume_download=True,
        ignore_patterns=['*.ckpt']
    )
    print('✅ Stable Diffusion v1.5 ダウンロード完了')
except Exception as e:
    print(f'❌ エラー: {e}')
"

echo ""
echo "📥 All-In-One Pixel Model をダウンロード中（約2GB）..."
python -c "
from huggingface_hub import snapshot_download
import os

cache_dir = os.path.expanduser('~/.cache/huggingface')

try:
    snapshot_download(
        'PublicPrompts/All-In-One-Pixel-Model',
        cache_dir=cache_dir,
        resume_download=True
    )
    print('✅ All-In-One Pixel Model ダウンロード完了')
except Exception as e:
    print(f'❌ エラー: {e}')
"

echo ""
echo "🎉 ダウンロード処理が完了しました！"
