#!/usr/bin/env python3
"""
pixel-art-styleモデルのテストスクリプト
"""
import requests
import json
import base64
from PIL import Image
import io

# APIエンドポイント
API_URL = "http://localhost:5001/generate"

# テストパラメータ
test_params = {
    "prompt": "pixelartstyle, cute cat character, simple design",
    "negative_prompt": "3d render, realistic, blurry, smooth shading",
    "model_id": "kohbanye/pixel-art-style",
    "width": 512,
    "height": 512,
    "pixel_size": 8,
    "palette_size": 16,
    "steps": 20,
    "guidance_scale": 7.5
}

print("🧪 pixel-art-styleモデルをテスト中...")
print(f"プロンプト: {test_params['prompt']}")

try:
    # APIリクエスト送信
    response = requests.post(API_URL, json=test_params)
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ 画像生成成功！")
            
            # 画像データをデコード
            image_data = data['image'].replace('data:image/png;base64,', '')
            image_bytes = base64.b64decode(image_data)
            
            # 画像を保存
            img = Image.open(io.BytesIO(image_bytes))
            output_path = "pixel_art_style_test.png"
            img.save(output_path)
            print(f"💾 画像を保存しました: {output_path}")
            
            # 画像情報
            print(f"📏 サイズ: {img.size}")
            print(f"🎨 モード: {img.mode}")
            
            # 真っ黒かチェック
            pixels = list(img.getdata())
            black_pixels = sum(1 for p in pixels if sum(p[:3]) < 30)
            black_ratio = black_pixels / len(pixels)
            
            if black_ratio > 0.95:
                print("⚠️  警告: 画像がほぼ真っ黒です！")
                print(f"   黒いピクセルの割合: {black_ratio*100:.1f}%")
            else:
                print(f"✨ 正常な画像です（黒いピクセル: {black_ratio*100:.1f}%）")
                
        else:
            print(f"❌ エラー: {data.get('error', 'Unknown error')}")
    else:
        print(f"❌ HTTPエラー: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ 接続エラー: {e}")
