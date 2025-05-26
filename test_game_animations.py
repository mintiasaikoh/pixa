#!/usr/bin/env python3
"""
実用的なゲーム開発向けアニメーションのテストスクリプト
"""

import sys
import os
from PIL import Image, ImageDraw
import numpy as np

# パスを追加してバックエンドモジュールをインポート
sys.path.append('./backend')

try:
    from services.animation_service import animation_service
    from services.gif_optimization_service import gif_optimization_service
    print("✓ animation_service モジュールを正常にインポートしました")
except ImportError as e:
    print(f"✗ インポートエラー: {e}")
    sys.exit(1)

def create_character_image(width=128, height=128):
    """ゲームキャラクター風のテスト画像を生成"""
    image = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # キャラクターのシルエット
    # 頭
    draw.ellipse([45, 20, 83, 50], fill=(255, 200, 150))  # 肌色の頭
    
    # 目
    draw.ellipse([52, 30, 58, 36], fill=(0, 0, 0))  # 左目
    draw.ellipse([70, 30, 76, 36], fill=(0, 0, 0))  # 右目
    
    # 口
    draw.arc([55, 38, 73, 46], 0, 180, fill=(255, 0, 0), width=2)
    
    # 体（胴体）
    draw.rectangle([55, 50, 73, 85], fill=(0, 100, 200))  # 青い服
    
    # 腕
    draw.rectangle([40, 55, 55, 75], fill=(255, 200, 150))  # 左腕
    draw.rectangle([73, 55, 88, 75], fill=(255, 200, 150))  # 右腕
    
    # 足
    draw.rectangle([58, 85, 68, 110], fill=(100, 50, 0))   # 左足
    draw.rectangle([70, 85, 80, 110], fill=(100, 50, 0))   # 右足
    
    # 靴
    draw.rectangle([55, 105, 72, 115], fill=(0, 0, 0))     # 左靴
    draw.rectangle([67, 105, 84, 115], fill=(0, 0, 0))     # 右靴
    
    return image

def test_game_animations():
    """ゲーム開発向けアニメーションのテスト"""
    print("\n=== ゲーム開発向けアニメーションテスト ===")
    
    # キャラクター画像を生成
    character_img = create_character_image()
    
    # テストするアニメーション
    game_animations = [
        'walk_cycle',      # 歩行サイクル
        'idle_breathing',  # アイドル（呼吸）
        'attack_slash',    # 攻撃（斬撃）
        'jump_landing',    # ジャンプ・着地
        'walk_4direction', # 4方向歩行
        'damage_flash',    # ダメージフラッシュ
    ]
    
    results = {}
    
    for anim_type in game_animations:
        try:
            print(f"\n🎮 {anim_type} アニメーション生成中...")
            
            # アニメーションフレーム生成
            frames = animation_service.create_animation_frames(
                base_image=character_img,
                animation_type=anim_type,
                frame_count=8,
                pixel_size=4,
                palette_size=16
            )
            
            if frames:
                # 差分合成最適化GIF保存
                output_path = f"game_animation_{anim_type}.gif"
                success, file_size = gif_optimization_service.save_optimized_gif(
                    frames=frames,
                    output_path=output_path,
                    duration=150,  # ゲームアニメーションは少し遅め
                    loop=0,
                    tolerance=2    # ゲームアニメーションは厳密に
                )
                
                if success:
                    results[anim_type] = {
                        'success': True,
                        'frames': len(frames),
                        'file_size': file_size,
                        'path': output_path
                    }
                    print(f"✓ 成功: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                else:
                    results[anim_type] = {
                        'success': False,
                        'error': 'GIF保存に失敗'
                    }
                    print("✗ GIF保存に失敗")
            else:
                results[anim_type] = {
                    'success': False,
                    'error': 'フレーム生成に失敗'
                }
                print("✗ フレーム生成に失敗")
                
        except Exception as e:
            results[anim_type] = {
                'success': False,
                'error': str(e)
            }
            print(f"✗ エラー: {e}")
    
    return results

def main():
    """メイン実行関数"""
    print("🎮 実用的なゲーム開発向けアニメーション差分合成テスト開始")
    
    try:
        # ゲーム開発向けアニメーションテスト
        game_results = test_game_animations()
        
        print(f"\n=== テスト結果サマリー ===")
        
        success_count = 0
        total_size = 0
        
        for anim_type, result in game_results.items():
            if result['success']:
                success_count += 1
                total_size += result['file_size']
                print(f"✓ {anim_type}: {result['file_size']:,} bytes")
            else:
                print(f"✗ {anim_type}: {result['error']}")
        
        print(f"\n📊 統計:")
        print(f"成功: {success_count}/{len(game_results)} アニメーション")
        print(f"合計サイズ: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        if success_count > 0:
            print(f"平均サイズ: {total_size/success_count:,.0f} bytes ({total_size/success_count/1024:.1f} KB)")
        
        print(f"\n🎉 ゲーム開発で使える実用的なアニメーションが生成されました！")
        print("生成されたGIFファイル:")
        for anim_type, result in game_results.items():
            if result['success']:
                print(f"  - {result['path']}")
        
    except Exception as e:
        print(f"✗ テスト中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
