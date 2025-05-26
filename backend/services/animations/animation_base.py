"""
Pixa - アニメーション基底クラス（簡素版）
"""
import math
from PIL import Image
from typing import List
import logging

logger = logging.getLogger(__name__)


class AnimationBase:
    """アニメーション生成の基底クラス"""
    
    @staticmethod
    def validate_parameters(base_image: Image.Image,
                          frame_count: int,
                          pixel_size: int,
                          palette_size: int) -> dict:
        """パラメータの検証と正規化"""
        if base_image is None:
            raise ValueError("Base image cannot be None")
        
        return {
            'frame_count': max(2, min(frame_count, 30)),
            'pixel_size': max(2, min(pixel_size, 20)),
            'palette_size': max(4, min(palette_size, 256)),
            'width': base_image.width,
            'height': base_image.height
        }
    
    @staticmethod
    def create_ease_in_out(t: float) -> float:
        """イージング関数: ease-in-out"""
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def create_ease_bounce(t: float) -> float:
        """イージング関数: bounce"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        else:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
    
    @staticmethod
    def create_safe_frame(base_image: Image.Image, 
                         width: int, 
                         height: int,
                         fill_color: tuple = (0, 0, 0)) -> Image.Image:
        """安全なフレーム作成"""
        try:
            return Image.new('RGB', (width, height), fill_color)
        except Exception as e:
            logger.error(f"Failed to create frame: {str(e)}")
            return base_image.copy()
    
    @staticmethod
    def apply_transform_safe(image: Image.Image,
                           transform_func,
                           fallback_image: Image.Image = None) -> Image.Image:
        """安全な変形適用"""
        try:
            return transform_func(image)
        except Exception as e:
            logger.error(f"Transform failed: {str(e)}")
            return fallback_image or image.copy()
    
    @staticmethod
    def apply_pixel_art_processing_to_frames(frames: List[Image.Image],
                                           pixel_size: int,
                                           palette_size: int) -> List[Image.Image]:
        """フレームリストにピクセルアート処理を適用（簡易版）"""
        processed_frames = []
        for frame in frames:
            # 簡易ピクセルアート処理
            if pixel_size > 1:
                # ダウンサンプル → アップサンプル
                small_size = (max(frame.width // pixel_size, 16), 
                             max(frame.height // pixel_size, 16))
                small_frame = frame.resize(small_size, Image.NEAREST)
                
                # カラーパレット制限
                if palette_size < 256:
                    small_frame = small_frame.quantize(colors=palette_size, dither=0)
                    small_frame = small_frame.convert('RGB')
                
                # 元サイズに戻す
                processed_frame = small_frame.resize(frame.size, Image.NEAREST)
            else:
                processed_frame = frame
            
            processed_frames.append(processed_frame)
        return processed_frames
