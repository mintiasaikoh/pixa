#!/usr/bin/env python3
"""
GIF差分合成最適化のテストスクリプト
"""

import sys
import os
from PIL import Image, ImageDraw
import numpy as np

# パスを追加してバックエンドモジュールをインポート
sys.path.append('./backend')

try:
    from creative_animations import (
        create_and_save_optimized_animation, 
        batch_create_optimized_animations,
        save_optimized_gif,
        create_creative_animation_frames
    )
    print("✓ creative_animations モジュールを正常にインポートしました")
except ImportError as e:
    print(f"✗ インポートエラー: {e}")
    sys.exit(1)

def create_test_image(width=128, height=128):
    """テスト用のシンプルなピクセルアート画像を生成"""
    image = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # シンプルなキャラクター風の図形
    # 顔の輪郭
    draw.ellipse([32, 32, 96, 96], fill=(255, 200, 150))
    
    # 目
    draw.ellipse([45, 50, 55, 60], fill=(0, 0, 0))
    draw.ellipse([73, 50, 83, 60], fill=(0, 0, 0))
    
    # 口
    draw.arc([50, 65, 78, 80], 0, 180, fill=(255, 0, 0), width=2)
    
    # ピクセルアート風に処理
    small = image.resize((32, 32), Image.NEAREST)
    pixel_art = small.resize((width, height), Image.NEAREST)
    
    return pixel_art

def test_single_animation():
    """単一アニメーションの差分合成テスト"""
    print("\n=== 単一アニメーション差分合成テスト ===")
    
    # テスト画像を生成
    test_img = create_test_image()
    
    # 通常のフレーム生成
    print("通常のフレーム生成...")
    normal_frames = create_creative_animation_frames(
        test_img, "heartbeat", 8, 8, 16
    )
    
    # 通常のGIF保存（比較用）
    normal_path = "test_normal_heartbeat.gif"
    normal_frames[0].save(
        normal_path,
        save_all=True,
        append_images=normal_frames[1:],
        duration=200,
        loop=0
    )
    normal_size = os.path.getsize(normal_path)
    
    # 差分合成最適化GIF保存
    print("差分合成最適化GIF生成...")
    optimized_frames, optimized_path = create_and_save_optimized_animation(
        base_image=test_img,
        animation_type="heartbeat",
        frame_count=8,
        output_path="test_optimized_heartbeat.gif",
        duration=200,
        tolerance=2  # より厳密な差分検出
    )
    optimized_size = os.path.getsize(optimized_path)
    
    # 結果比較
    print(f"\n結果比較:")
    print(f"通常のGIF: {normal_size:,} bytes ({normal_size/1024:.1f} KB)")
    print(f"最適化GIF: {optimized_size:,} bytes ({optimized_size/1024:.1f} KB)")
    print(f"削減率: {((normal_size - optimized_size) / normal_size * 100):.1f}%")
    
    return normal_size, optimized_size

def test_batch_animations():
    """一括アニメーション生成テスト"""
    print("\n=== 一括アニメーション差分合成テスト ===")
    
    # テスト画像を生成
    test_img = create_test_image()
    
    # 一括生成
    results = batch_create_optimized_animations(
        base_image=test_img,
        output_dir="./test_outputs/",
        pixel_size=8,
        palette_size=16
    )
    
    # 結果表示
    print(f"\n生成結果:")
    total_size = 0
    success_count = 0
    
    for anim_type, result in results.items():
        if result['success']:
            file_size = os.path.getsize(result['path'])
            total_size += file_size
            success_count += 1
            print(f"✓ {anim_type}: {file_size:,} bytes")
        else:
            print(f"✗ {anim_type}: {result['error']}")
    
    print(f"\n統計:")
    print(f"成功: {success_count}/{len(results)} アニメーション")
    print(f"合計サイズ: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    return results

def main():
    """メイン実行関数"""
    print("Pixa GIF差分合成最適化テスト開始")
    
    # 出力ディレクトリ作成
    os.makedirs("test_outputs", exist_ok=True)
    
    try:
        # 単一アニメーションテスト
        normal_size, optimized_size = test_single_animation()
        
        # 一括アニメーションテスト
        batch_results = test_batch_animations()
        
        print(f"\n=== テスト完了 ===")
        print(f"差分合成最適化により平均 {((normal_size - optimized_size) / normal_size * 100):.1f}% のサイズ削減を達成")
        
    except Exception as e:
        print(f"✗ テスト中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
