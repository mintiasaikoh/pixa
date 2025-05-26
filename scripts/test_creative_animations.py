#!/usr/bin/env python3
"""
創造的なアニメーション機能のテストスクリプト
新しい面白い動きを確認
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from PIL import Image
from creative_animations import create_creative_animation_frames
import time

def test_creative_animations():
    print("🎉 創造的なアニメーションテスト開始...")
    
    # テスト用の画像を作成（カラフルなピクセルアート）
    size = 128
    test_image = Image.new('RGB', (size, size), (0, 0, 0))
    
    # カラフルなパターンを描画
    pixels = test_image.load()
    colors = [
        (255, 0, 0),    # 赤
        (0, 255, 0),    # 緑
        (0, 0, 255),    # 青
        (255, 255, 0),  # 黄
        (255, 0, 255),  # マゼンタ
        (0, 255, 255),  # シアン
    ]
    
    # チェッカーボードパターン
    block_size = 16
    for y in range(0, size, block_size):
        for x in range(0, size, block_size):
            color = colors[((x // block_size) + (y // block_size)) % len(colors)]
            for dy in range(block_size):
                for dx in range(block_size):
                    if x + dx < size and y + dy < size:
                        pixels[x + dx, y + dy] = color
    
    # 各アニメーションタイプをテスト
    animation_types = [
        ("glitch_wave", "グリッチウェーブ"),
        ("explode_reassemble", "爆発＆再集合"),
        ("pixel_rain", "ピクセルレイン"),
        ("wave_distortion", "波状歪み"),
        ("heartbeat", "ハートビート"),
        ("spiral", "スパイラル"),
        ("split_merge", "分裂＆結合"),
        ("electric_shock", "電撃エフェクト"),
        ("rubberband", "ラバーバンド")
    ]
    
    for anim_type, name in animation_types:
        print(f"\n✨ {name} ({anim_type}) をテスト中...")
        start_time = time.time()
        
        try:
            # アニメーションフレームを生成
            frames = create_creative_animation_frames(
                test_image,
                anim_type,
                frame_count=8,
                pixel_size=8,
                palette_size=16
            )
            
            # GIFとして保存
            filename = f"test_animation_{anim_type}.gif"
            frames[0].save(
                filename,
                save_all=True,
                append_images=frames[1:],
                duration=100,  # 100ms per frame
                loop=0
            )
            
            elapsed_time = time.time() - start_time
            print(f"✅ 成功: {filename} ({elapsed_time:.2f}秒)")
            print(f"   フレーム数: {len(frames)}")
            
        except Exception as e:
            print(f"❌ エラー: {str(e)}")
    
    print("\n🎉 テスト完了！")
    print("\n💡 ヒント: 生成されたGIFファイルを確認してください。")
    print("   各アニメーションの動きを楽しんでください！")

if __name__ == "__main__":
    test_creative_animations()
