#!/usr/bin/env python3
"""
必須モデルを自動ダウンロードするスクリプト
インタラクションなしで実行可能
"""

import os
import sys
from pathlib import Path

# 必須モデルのみに絞る
ESSENTIAL_MODELS = [
    {
        "id": "runwayml/stable-diffusion-v1-5",
        "name": "Stable Diffusion v1.5"
    },
    {
        "id": "PublicPrompts/All-In-One-Pixel-Model",
        "name": "All-In-One Pixel Model（推奨）"
    }
]

def main():
    print("🎨 Pixa - 必須モデルの自動ダウンロード")
    print("📥 基本的なモデル（約6GB）をダウンロードします...\n")
    
    try:
        from huggingface_hub import snapshot_download
        
        cache_dir = os.environ.get('HF_HOME', os.path.expanduser('~/.cache/huggingface'))
        
        for model in ESSENTIAL_MODELS:
            print(f"\n📦 {model['name']} をダウンロード中...")
            print(f"   ID: {model['id']}")
            
            try:
                # モデルをダウンロード
                snapshot_download(
                    repo_id=model['id'],
                    cache_dir=cache_dir,
                    resume_download=True,
                    ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
                )
                print(f"✅ {model['name']} のダウンロード完了！")
            except Exception as e:
                print(f"⚠️  {model['name']} のダウンロード中にエラー: {e}")
                print("   後で手動でダウンロードしてください")
        
        print("\n🎉 必須モデルのダウンロードが完了しました！")
        print("   ./start_server.sh でサーバーを起動できます")
        
    except ImportError:
        print("❌ huggingface_hubがインストールされていません")
        print("   pip install huggingface-hub を実行してください")
        sys.exit(1)

if __name__ == "__main__":
    main()
