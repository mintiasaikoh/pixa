#!/usr/bin/env python3
"""
アニメーション生成機能のテストスクリプト
"""

import requests
import json
import time
import base64
from PIL import Image
from io import BytesIO

# APIのURL
API_URL = "http://localhost:5001"

def test_server_health():
    """サーバーの健全性チェック"""
    print("1. サーバー健全性チェック...")
    try:
        response = requests.get(f"{API_URL}/health")
        data = response.json()
        print(f"   状態: {data['status']}")
        print(f"   パイプライン読み込み: {data['pipeline_loaded']}")
        print(f"   デバイス: {data['device']}")
        return data['pipeline_loaded']
    except Exception as e:
        print(f"   エラー: {e}")
        return False

def test_static_image_generation():
    """静止画生成テスト"""
    print("\n2. 静止画生成テスト...")
    params = {
        "prompt": "cute pixel art cat",
        "width": 512,
        "height": 512,
        "pixel_size": 8,
        "palette_size": 16,
        "steps": 20
    }
    
    try:
        response = requests.post(f"{API_URL}/generate", json=params)
        data = response.json()
        
        if data.get('success'):
            print("   ✓ 静止画生成成功")
            # 画像をデコードして保存
            image_data = data['image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            img = Image.open(BytesIO(image_bytes))
            img.save("test_static.png")
            print("   → test_static.png として保存")
            return True
        else:
            print(f"   × 生成失敗: {data.get('error')}")
            return False
    except Exception as e:
        print(f"   × エラー: {e}")
        return False

def test_animation_generation(animation_type="idle"):
    """アニメーション生成テスト"""
    print(f"\n3. アニメーション生成テスト (タイプ: {animation_type})...")
    params = {
        "prompt": "cute pixel art cat walking",
        "animation_type": animation_type,
        "frame_count": 4,
        "fps": 10,
        "width": 512,
        "height": 512,
        "pixel_size": 8,
        "palette_size": 16,
        "steps": 20
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/generate_animation", json=params)
        elapsed_time = time.time() - start_time
        
        data = response.json()
        
        if data.get('success'):
            print(f"   ✓ アニメーション生成成功 (所要時間: {elapsed_time:.2f}秒)")
            print(f"   → タイプ: {data['animation_type']}")
            print(f"   → フレーム数: {data['frame_count']}")
            print(f"   → FPS: {data['fps']}")
            
            # GIFをデコードして保存
            gif_data = data['image'].split(',')[1]
            gif_bytes = base64.b64decode(gif_data)
            
            filename = f"test_animation_{animation_type}.gif"
            with open(filename, 'wb') as f:
                f.write(gif_bytes)
            print(f"   → {filename} として保存")
            return True
        else:
            print(f"   × 生成失敗: {data.get('error')}")
            return False
    except Exception as e:
        print(f"   × エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=== Pixa アニメーション機能テスト ===\n")
    
    # 1. サーバー健全性チェック
    if not test_server_health():
        print("\n❌ サーバーが正常に動作していません。")
        print("   ./start_server.sh でサーバーを起動してください。")
        return
    
    # 2. 静止画生成テスト
    if not test_static_image_generation():
        print("\n❌ 静止画生成に失敗しました。")
        return
    
    # 3. 各種アニメーションタイプのテスト
    animation_types = ["idle", "walk", "bounce", "glow", "rotate"]
    success_count = 0
    
    for anim_type in animation_types:
        if test_animation_generation(anim_type):
            success_count += 1
        time.sleep(2)  # サーバーの負荷を考慮
    
    # 結果サマリー
    print(f"\n=== テスト結果 ===")
    print(f"✓ 成功: {success_count}/{len(animation_types)} アニメーションタイプ")
    print(f"\n生成されたファイル:")
    print("  - test_static.png (静止画)")
    for anim_type in animation_types:
        print(f"  - test_animation_{anim_type}.gif")

if __name__ == "__main__":
    main()