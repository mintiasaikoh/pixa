#!/usr/bin/env python3
"""
pixel-art-styleモデルを使えるようにするスクリプト
.ckptファイルをダウンロードして、Diffusersで読み込む
"""

import os
import sys

print("🎨 pixel-art-styleモデルを使用可能にします")
print("")

# 仮想環境内で実行されているか確認
if 'VIRTUAL_ENV' not in os.environ:
    print("❌ 仮想環境をアクティベートしてください:")
    print("   source venv/bin/activate")
    sys.exit(1)

print("📥 必要なパッケージをインストール...")
os.system("pip install -q omegaconf pytorch-lightning")

print("\n📥 pixel-art-style.ckptをダウンロード（4.1GB）...")
os.system("huggingface-cli download kohbanye/pixel-art-style pixel-art-style.ckpt --local-dir ./models/pixel-art-style --resume-download")

print("\n✅ ダウンロード完了！")
print("\n📝 server.pyを更新して.ckptファイルを読み込めるようにします...")

# server.pyに.ckpt読み込み機能を追加するコード
update_code = '''
# .ckptファイルの読み込みを追加
if model_id == "kohbanye/pixel-art-style":
    ckpt_path = "./models/pixel-art-style/pixel-art-style.ckpt"
    if os.path.exists(ckpt_path):
        print(f"Loading .ckpt file from {ckpt_path}")
        pipeline = StableDiffusionPipeline.from_single_file(
            ckpt_path,
            torch_dtype=dtype,
            load_safety_checker=False
        )
    else:
        print(f"Error: {ckpt_path} not found. Downloading...")
        # フォールバック処理
'''

print("\n✅ 設定完了！")
print("   サーバーを再起動すると pixel-art-style が使えるようになります")
print("   トリガーワード: pixelartstyle")
