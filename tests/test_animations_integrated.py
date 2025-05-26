#!/usr/bin/env python3
"""
Pixa - 統合アニメーションテストスイート
リファクタリング後の総合テスト
"""

import sys
import os
import unittest
from pathlib import Path

# パスを追加してバックエンドモジュールをインポート
sys.path.append('../backend')

try:
    from services.animations import AnimationFactory
    from services.gif_optimization_service import gif_optimization_service
    from utils.image_utils import apply_pixel_art_processing
    print("✓ リファクタリング後のモジュールを正常にインポートしました")
except ImportError as e:
    print(f"✗ インポートエラー: {e}")
    sys.exit(1)

from PIL import Image, ImageDraw


class TestAnimationSuite(unittest.TestCase):
    """アニメーション統合テストスイート"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス全体の初期化"""
        cls.test_image = cls.create_test_character()
        cls.output_dir = Path('./outputs')
        cls.output_dir.mkdir(exist_ok=True)
    
    @staticmethod
    def create_test_character(width=128, height=128):
        """テスト用キャラクター画像を生成"""
        image = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # シンプルなキャラクター
        draw.ellipse([45, 20, 83, 50], fill=(255, 200, 150))  # 頭
        draw.ellipse([52, 30, 58, 36], fill=(0, 0, 0))        # 左目
        draw.ellipse([70, 30, 76, 36], fill=(0, 0, 0))        # 右目
        draw.rectangle([55, 50, 73, 85], fill=(0, 100, 200))  # 体
        draw.rectangle([40, 55, 55, 75], fill=(255, 200, 150)) # 左腕
        draw.rectangle([73, 55, 88, 75], fill=(255, 200, 150)) # 右腕
        draw.rectangle([58, 85, 68, 110], fill=(100, 50, 0))   # 左足
        draw.rectangle([70, 85, 80, 110], fill=(100, 50, 0))   # 右足
        
        return image
    
    def test_game_animations(self):
        """ゲーム開発向けアニメーションのテスト"""
        game_types = AnimationFactory.get_animation_types_by_category('game')
        
        results = {}
        for anim_type in game_types:
            with self.subTest(animation_type=anim_type):
                # フレーム生成
                frames = AnimationFactory.create_animation_frames(
                    base_image=self.test_image,
                    animation_type=anim_type,
                    frame_count=8,
                    pixel_size=4,
                    palette_size=16
                )
                
                # アサーション
                self.assertIsInstance(frames, list)
                self.assertGreater(len(frames), 0)
                self.assertEqual(len(frames), 8)
                
                for frame in frames:
                    self.assertIsInstance(frame, Image.Image)
                    self.assertEqual(frame.size, self.test_image.size)
                
                # GIF保存テスト
                output_path = self.output_dir / f"test_{anim_type}.gif"
                success, file_size = gif_optimization_service.save_optimized_gif(
                    frames=frames,
                    output_path=str(output_path),
                    duration=150,
                    tolerance=2
                )
                
                self.assertTrue(success)
                self.assertIsInstance(file_size, int)
                self.assertGreater(file_size, 0)
                
                results[anim_type] = {
                    'frames': len(frames),
                    'file_size': file_size,
                    'success': True
                }
        
        print(f"\n🎮 ゲーム開発向けアニメーションテスト結果:")
        for anim_type, result in results.items():
            print(f"  ✓ {anim_type}: {result['file_size']:,} bytes")
    
    def test_effect_animations(self):
        """エフェクト系アニメーションのテスト"""
        effect_types = AnimationFactory.get_animation_types_by_category('effect')
        
        results = {}
        for anim_type in effect_types:
            with self.subTest(animation_type=anim_type):
                # フレーム生成
                frames = AnimationFactory.create_animation_frames(
                    base_image=self.test_image,
                    animation_type=anim_type,
                    frame_count=8,
                    pixel_size=4,
                    palette_size=16
                )
                
                # アサーション
                self.assertIsInstance(frames, list)
                self.assertGreater(len(frames), 0)
                
                for frame in frames:
                    self.assertIsInstance(frame, Image.Image)
                
                # GIF保存テスト
                output_path = self.output_dir / f"test_{anim_type}.gif"
                success, file_size = gif_optimization_service.save_optimized_gif(
                    frames=frames,
                    output_path=str(output_path),
                    duration=100,
                    tolerance=3
                )
                
                self.assertTrue(success)
                self.assertIsInstance(file_size, int)
                self.assertGreater(file_size, 0)
                
                results[anim_type] = {
                    'frames': len(frames),
                    'file_size': file_size,
                    'success': True
                }
        
        print(f"\n🎨 エフェクト系アニメーションテスト結果:")
        for anim_type, result in results.items():
            print(f"  ✓ {anim_type}: {result['file_size']:,} bytes")
    
    def test_animation_factory(self):
        """AnimationFactoryの統合テスト"""
        # 全アニメーション種類の取得
        all_types = AnimationFactory.get_all_animation_types()
        self.assertIsInstance(all_types, list)
        self.assertGreater(len(all_types), 10)
        
        # アニメーション情報の取得
        for anim_type in all_types[:3]:  # 最初の3つをテスト
            info = AnimationFactory.get_animation_info(anim_type)
            self.assertIsInstance(info, dict)
            self.assertIn('name', info)
            self.assertIn('category', info)
            self.assertIn('description', info)
        
        print(f"\n🏭 AnimationFactory統合テスト:")
        print(f"  ✓ サポート種類数: {len(all_types)}")
        print(f"  ✓ ゲーム系: {len(AnimationFactory.get_animation_types_by_category('game'))}")
        print(f"  ✓ エフェクト系: {len(AnimationFactory.get_animation_types_by_category('effect'))}")
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なアニメーション種類
        frames = AnimationFactory.create_animation_frames(
            base_image=self.test_image,
            animation_type="invalid_type",
            frame_count=4
        )
        self.assertIsInstance(frames, list)
        self.assertGreater(len(frames), 0)  # デフォルトアニメーションが返される
        
        # None画像（エラーになるはず）
        with self.assertRaises(Exception):
            AnimationFactory.create_animation_frames(
                base_image=None,
                animation_type="walk_cycle"
            )
        
        print(f"\n🛡️ エラーハンドリングテスト:")
        print(f"  ✓ 無効なアニメーション種類の処理")
        print(f"  ✓ None画像の適切なエラー処理")


def run_performance_test():
    """パフォーマンステスト"""
    print(f"\n⚡ パフォーマンステスト:")
    
    import time
    test_image = TestAnimationSuite.create_test_character()
    
    # 各カテゴリの実行時間測定
    game_types = AnimationFactory.get_animation_types_by_category('game')
    effect_types = AnimationFactory.get_animation_types_by_category('effect')
    
    start_time = time.time()
    for anim_type in game_types:
        frames = AnimationFactory.create_animation_frames(
            base_image=test_image,
            animation_type=anim_type,
            frame_count=8
        )
    game_time = time.time() - start_time
    
    start_time = time.time()
    for anim_type in effect_types:
        frames = AnimationFactory.create_animation_frames(
            base_image=test_image,
            animation_type=anim_type,
            frame_count=8
        )
    effect_time = time.time() - start_time
    
    print(f"  ✓ ゲーム系アニメーション: {game_time:.2f}秒 ({len(game_types)}種類)")
    print(f"  ✓ エフェクト系アニメーション: {effect_time:.2f}秒 ({len(effect_types)}種類)")
    print(f"  ✓ 合計実行時間: {game_time + effect_time:.2f}秒")


if __name__ == '__main__':
    print("🧪 Pixa アニメーション統合テストスイート開始")
    print("=" * 50)
    
    # ユニットテスト実行
    unittest.main(verbosity=2, exit=False)
    
    # パフォーマンステスト実行
    run_performance_test()
    
    print("=" * 50)
    print("🎉 全テスト完了！")
