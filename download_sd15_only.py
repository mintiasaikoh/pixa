#!/usr/bin/env python3
"""最小限のモデルダウンロード - SD1.5のみ"""

import os
import subprocess
import sys

print("🎨 Pixa - 最小限モデルダウンロード")
print("📥 Stable Diffusion v1.5のみダウンロードします（約4GB）")
print("")

# huggingface-cliを使用
try:
    # SD 1.5をダウンロード
    cmd = [
        sys.executable, "-m", "huggingface_hub", "download",
        "runwayml/stable-diffusion-v1-5",
        "--resume-download",
        "--local-dir-use-symlinks", "False"
    ]
    
    print("🔽 ダウンロード開始...")
    print("   これには数分かかる場合があります")
    print("   進捗はターミナルで確認できます")
    print("")
    
    subprocess.run(cmd)
    
    print("\n✅ ダウンロード完了！")
    print("   サーバーを再起動してください")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    print("   手動でダウンロードしてください：")
    print("   huggingface-cli download runwayml/stable-diffusion-v1-5")
