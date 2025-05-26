#!/usr/bin/env python3
"""
グリッチアートジェネレーターのテストスクリプト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from glitch_art_generator import GlitchArtGenerator
from PIL import Image
import time

def test_glitch_art():
    print("🎨 グリッチアートジェネレーターテスト開始...")
    
    # ジェネレーター初期化
    generator = GlitchArtGenerator(512, 512)
    
    # 各スタイルをテスト
    styles = ['full', 'lines', 'geometric', 'ascii', 'noise']
    
    for style in styles:
        print(f"\n✨ スタイル '{style}' をテスト中...")
        start_time = time.time()
        
        try:
            # 静止画生成
            image = generator.generate(style)
            
            # 保存
            filename = f"glitch_test_{style}.png"
            image.save(filename)
            
            elapsed_time = time.time() - start_time
            print(f"✅ 成功: {filename} ({elapsed_time:.2f}秒)")
            
        except Exception as e:
            print(f"❌ エラー: {str(e)}")
    
    # アニメーションテスト
    print(f"\n🎬 アニメーションをテスト中...")
    start_time = time.time()
    
    try:
        frames = generator.generate_animated_frames(8)
        
        # GIFとして保存
        frames[0].save(
            'glitch_test_animation.gif',
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ アニメーション成功: glitch_test_animation.gif ({elapsed_time:.2f}秒)")
        
    except Exception as e:
        print(f"❌ アニメーションエラー: {str(e)}")
    
    print("\n✨ テスト完了!")

if __name__ == "__main__":
    test_glitch_art()
