#!/usr/bin/env python3
"""
実際にダウンロード済みのモデルを確認して、model_configs.pyを更新
"""

import os
import subprocess

print("🔍 ダウンロード済みモデルを確認中...")

# Hugging Faceキャッシュをチェック
cache_dir = os.path.expanduser("~/.cache/huggingface/hub/")

# 実際に存在するモデルをチェック
available_models = []

# 1. 通常のモデル
model_checks = [
    ("runwayml/stable-diffusion-v1-5", "models--runwayml--stable-diffusion-v1-5"),
    ("PublicPrompts/All-In-One-Pixel-Model", "models--PublicPrompts--All-In-One-Pixel-Model"),
    ("Onodofthenorth/SD_PixelArt_SpriteSheet_Generator", "models--Onodofthenorth--SD_PixelArt_SpriteSheet_Generator"),
    ("wavymulder/Analog-Diffusion", "models--wavymulder--Analog-Diffusion"),
    ("nerijs/pixel-art-xl", "models--nerijs--pixel-art-xl"),
    ("stabilityai/stable-diffusion-xl-base-1.0", "models--stabilityai--stable-diffusion-xl-base-1.0"),
    ("pixelparty/pixel-party-xl", "models--pixelparty--pixel-party-xl"),
]

print("\n📊 モデルステータス:")
for model_id, cache_name in model_checks:
    path = os.path.join(cache_dir, cache_name)
    if os.path.exists(path):
        print(f"✅ {model_id}")
        available_models.append(model_id)
    else:
        print(f"❌ {model_id} - 未ダウンロード")

# 2. pixel-art-styleの特別チェック（.ckptファイル）
ckpt_path = "./models/pixel-art-style/pixel-art-style.ckpt"
if os.path.exists(ckpt_path):
    print(f"✅ kohbanye/pixel-art-style (.ckpt)")
    available_models.append("kohbanye/pixel-art-style")
else:
    print(f"❌ kohbanye/pixel-art-style - .ckptファイル未ダウンロード")

print(f"\n📦 利用可能なモデル数: {len(available_models)}")
print("\n💡 未ダウンロードのモデルを非表示にするには、model_configs.pyを更新してください")
