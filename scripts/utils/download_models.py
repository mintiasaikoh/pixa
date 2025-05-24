#!/usr/bin/env python3
"""
Pixaで使用するモデルをダウンロードするスクリプト
Hugging Faceから必要なモデルファイルを事前にダウンロードします
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download
import torch

# モデル保存ディレクトリ
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# ダウンロードするモデルのリスト
MODELS_TO_DOWNLOAD = [
    {
        "id": "runwayml/stable-diffusion-v1-5",
        "name": "Stable Diffusion v1.5（標準）",
        "type": "full",
        "size": "~4GB"
    },
    {
        "id": "PublicPrompts/All-In-One-Pixel-Model", 
        "name": "All-In-One Pixel Model（推奨）",
        "type": "full",
        "size": "~2GB"
    },
    {
        "id": "Onodofthenorth/SD_PixelArt_SpriteSheet_Generator",
        "name": "スプライトシート生成",
        "type": "full", 
        "size": "~2GB"
    },
    {
        "id": "kohbanye/pixel-art-style",
        "name": "Pixel Art Style",
        "type": "full",
        "size": "~2GB"
    },
    {
        "id": "wavymulder/Analog-Diffusion",
        "name": "Analog Diffusion（レトロ風）",
        "type": "full",
        "size": "~2GB"
    },
    {
        "id": "stabilityai/stable-diffusion-xl-base-1.0",
        "name": "SDXL Base（LoRA用ベースモデル）",
        "type": "full",
        "size": "~7GB"
    },
    {
        "id": "nerijs/pixel-art-xl",
        "name": "Pixel Art XL LoRA",
        "type": "lora",
        "size": "~200MB"
    },
    {
        "id": "latent-consistency/lcm-lora-sdxl",
        "name": "LCM LoRA（高速化用）",
        "type": "lora",
        "size": "~200MB"
    },
    {
        "id": "pixelparty/pixel-party-xl",
        "name": "Pixel Party XL（UNetのみ）",
        "type": "unet",
        "size": "~5GB"
    }
]

def get_cache_dir():
    """Hugging Faceのキャッシュディレクトリを取得"""
    cache_dir = os.environ.get('HF_HOME', os.path.expanduser('~/.cache/huggingface'))
    return cache_dir

def download_model(model_info):
    """モデルをダウンロード"""
    model_id = model_info["id"]
    model_name = model_info["name"]
    model_type = model_info["type"]
    model_size = model_info["size"]
    
    print(f"\n{'='*60}")
    print(f"📦 モデル: {model_name}")
    print(f"   ID: {model_id}")
    print(f"   サイズ: {model_size}")
    print(f"   タイプ: {model_type}")
    print(f"{'='*60}")
    
    try:
        cache_dir = get_cache_dir()
        
        if model_type == "lora":
            # LoRAファイルのみダウンロード
            print("🔽 LoRAファイルをダウンロード中...")
            files = ["pytorch_lora_weights.safetensors", "pytorch_lora_weights.bin"]
            downloaded = False
            
            for file in files:
                try:
                    hf_hub_download(
                        repo_id=model_id,
                        filename=file,
                        cache_dir=cache_dir,
                        resume_download=True
                    )
                    downloaded = True
                    break
                except Exception:
                    continue
                    
            if not downloaded:
                # 全ファイルをダウンロード（フォールバック）
                snapshot_download(
                    repo_id=model_id,
                    cache_dir=cache_dir,
                    resume_download=True,
                    ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
                )
                
        elif model_type == "unet":
            # UNetモデルのみダウンロード
            print("🔽 UNetモデルをダウンロード中...")
            snapshot_download(
                repo_id=model_id,
                cache_dir=cache_dir,
                resume_download=True,
                ignore_patterns=["*.msgpack", "*.h5", "*.ot", "vae/*", "text_encoder/*", "tokenizer/*"]
            )
            
        else:
            # フルモデルをダウンロード
            print("🔽 フルモデルをダウンロード中...")
            # SD1.5かSDXLかを判定
            variant = "fp16" if torch.cuda.is_available() or torch.backends.mps.is_available() else None
            
            snapshot_download(
                repo_id=model_id,
                cache_dir=cache_dir,
                resume_download=True,
                variant=variant,
                ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
            )
        
        print(f"✅ {model_name} のダウンロードが完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {model_name} のダウンロードに失敗しました")
        print(f"   詳細: {str(e)}")
        return False

def main():
    print("🎨 Pixa - AIピクセルアートジェネレーター")
    print("📥 必要なモデルのダウンロードを開始します\n")
    
    # キャッシュディレクトリの確認
    cache_dir = get_cache_dir()
    print(f"💾 モデルの保存先: {cache_dir}")
    
    # 合計サイズの概算
    print(f"\n⚠️  注意: 全モデルで約25GB必要です")
    print("   既にダウンロード済みのモデルはスキップされます")
    
    # ユーザーに確認
    response = input("\n続行しますか？ [Y/n]: ").strip().lower()
    if response == 'n':
        print("❌ ダウンロードをキャンセルしました")
        return
    
    # 選択的ダウンロード
    print("\n📋 ダウンロードするモデルを選択してください:")
    print("   1. 必須モデルのみ（SD1.5 + All-In-One）約6GB")
    print("   2. 推奨モデル（上記 + LoRA）約7GB") 
    print("   3. 全モデル 約25GB")
    print("   4. カスタム選択")
    
    choice = input("\n選択 [1-4]: ").strip()
    
    models_to_download = []
    
    if choice == "1":
        # 必須モデルのみ
        models_to_download = [m for m in MODELS_TO_DOWNLOAD if m["id"] in [
            "runwayml/stable-diffusion-v1-5",
            "PublicPrompts/All-In-One-Pixel-Model"
        ]]
    elif choice == "2":
        # 推奨モデル
        models_to_download = [m for m in MODELS_TO_DOWNLOAD if m["id"] in [
            "runwayml/stable-diffusion-v1-5",
            "PublicPrompts/All-In-One-Pixel-Model",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "nerijs/pixel-art-xl",
            "latent-consistency/lcm-lora-sdxl"
        ]]
    elif choice == "3":
        # 全モデル
        models_to_download = MODELS_TO_DOWNLOAD
    elif choice == "4":
        # カスタム選択
        print("\nダウンロードするモデルを選択してください（複数選択可）:")
        for i, model in enumerate(MODELS_TO_DOWNLOAD):
            print(f"  {i+1}. {model['name']} ({model['size']})")
        
        selections = input("\n番号をカンマ区切りで入力 (例: 1,2,5): ").strip()
        try:
            indices = [int(x.strip())-1 for x in selections.split(",")]
            models_to_download = [MODELS_TO_DOWNLOAD[i] for i in indices if 0 <= i < len(MODELS_TO_DOWNLOAD)]
        except:
            print("❌ 無効な選択です")
            return
    else:
        print("❌ 無効な選択です")
        return
    
    # ダウンロード実行
    success_count = 0
    fail_count = 0
    
    for model in models_to_download:
        if download_model(model):
            success_count += 1
        else:
            fail_count += 1
    
    # 結果表示
    print(f"\n{'='*60}")
    print(f"📊 ダウンロード結果:")
    print(f"   ✅ 成功: {success_count} モデル")
    print(f"   ❌ 失敗: {fail_count} モデル")
    print(f"{'='*60}")
    
    if success_count > 0:
        print("\n🎉 モデルのダウンロードが完了しました！")
        print("   サーバーを起動してPixaをお楽しみください:")
        print("   $ ./start_server.sh")

if __name__ == "__main__":
    main()
