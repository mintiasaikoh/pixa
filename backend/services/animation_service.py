"""
Pixa - アニメーション生成サービス
"""
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
from typing import List, Optional, Tuple
import logging

from utils.image_utils import apply_pixel_art_processing

logger = logging.getLogger(__name__)


class AnimationService:
    """アニメーション生成サービス"""
    
    @staticmethod
    def create_animation_frames(base_image: Image.Image,
                              animation_type: str,
                              frame_count: int = 8,
                              pixel_size: int = 8,
                              palette_size: int = 16) -> List[Image.Image]:
        """アニメーションフレームを生成"""
        
        if base_image is None:
            return []
        
        frames = []
        width, height = base_image.size
        
        try:
            if animation_type == "glitch_wave":
                frames = AnimationService._create_glitch_wave_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "explode_reassemble":
                frames = AnimationService._create_explode_reassemble_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "pixel_rain":
                frames = AnimationService._create_pixel_rain_frames(
                    base_image, frame_count, width, height, pixel_size
                )
            elif animation_type == "wave_distortion":
                frames = AnimationService._create_wave_distortion_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "heartbeat":
                frames = AnimationService._create_heartbeat_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "spiral":
                frames = AnimationService._create_spiral_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "split_merge":
                frames = AnimationService._create_split_merge_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "electric_shock":
                frames = AnimationService._create_electric_shock_frames(
                    base_image, frame_count, width, height
                )
            else:  # デフォルト: rubberband
                frames = AnimationService._create_rubberband_frames(
                    base_image, frame_count, width, height
                )
            
            # 各フレームにピクセルアート処理を適用
            processed_frames = []
            for frame in frames:
                processed_frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
                processed_frames.append(processed_frame)
            
            return processed_frames
        
        except Exception as e:
            logger.error(f"Animation creation failed: {str(e)}")
            return [base_image]  # エラー時は元画像を返す
    
    @staticmethod
    def _create_glitch_wave_frames(base_image: Image.Image, 
                                  frame_count: int, 
                                  width: int, 
                                  height: int) -> List[Image.Image]:
        """グリッチウェーブフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            
            # 各行をランダムにシフト
            for y in range(0, height, 8):
                shift = int(10 * math.sin(2 * math.pi * (i / frame_count + y / height)))
                if random.random() > 0.7:  # たまに大きくグリッチ
                    shift += random.randint(-20, 20)
                
                # 行をシフト
                if y < height:
                    pixels[y:min(y+8, height)] = np.roll(pixels[y:min(y+8, height)], shift, axis=1)
            
            frame = Image.fromarray(pixels.astype('uint8'))
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_heartbeat_frames(base_image: Image.Image,
                               frame_count: int,
                               width: int,
                               height: int) -> List[Image.Image]:
        """ハートビートフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            t = i / frame_count
            # ハートビートパターン（2回の拍動）
            if t < 0.2:
                scale = 1 + 0.1 * (t / 0.2)
            elif t < 0.3:
                scale = 1.1 - 0.1 * ((t - 0.2) / 0.1)
            elif t < 0.4:
                scale = 1 + 0.15 * ((t - 0.3) / 0.1)
            elif t < 0.5:
                scale = 1.15 - 0.15 * ((t - 0.4) / 0.1)
            else:
                scale = 1
            
            # スケール変更
            new_size = (int(width * scale), int(height * scale))
            scaled = base_image.resize(new_size, Image.NEAREST)
            
            # 中央に配置
            frame = Image.new('RGB', base_image.size, (0, 0, 0))
            x_offset = (width - new_size[0]) // 2
            y_offset = (height - new_size[1]) // 2
            frame.paste(scaled, (x_offset, y_offset))
            
            frames.append(frame)
        
        return frames
    
    # 他のアニメーション生成メソッドも同様に実装...
    # （省略して、必要に応じて追加）


# グローバルサービスインスタンス
animation_service = AnimationService()
