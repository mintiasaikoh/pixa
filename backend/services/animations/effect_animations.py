"""
Pixa - エフェクト系アニメーション
"""
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
from typing import List
import logging

from .animation_base import AnimationBase

logger = logging.getLogger(__name__)


class EffectAnimations(AnimationBase):
    """エフェクト系アニメーション生成クラス"""
    
    @staticmethod
    def create_frames(base_image: Image.Image,
                     animation_type: str,
                     frame_count: int = 8,
                     pixel_size: int = 8,
                     palette_size: int = 16,
                     **kwargs) -> List[Image.Image]:
        """エフェクト系アニメーションフレーム生成"""
        
        # パラメータ検証
        params = EffectAnimations.validate_parameters(base_image, frame_count, pixel_size, palette_size)
        width, height = params['width'], params['height']
        frame_count = params['frame_count']
        
        try:
            # アニメーション種類別の処理
            if animation_type == "glitch_wave":
                frames = EffectAnimations._create_glitch_wave_frames(base_image, frame_count, width, height)
            elif animation_type == "heartbeat":
                frames = EffectAnimations._create_heartbeat_frames(base_image, frame_count, width, height)
            elif animation_type == "spiral":
                frames = EffectAnimations._create_spiral_frames(base_image, frame_count, width, height)
            elif animation_type == "pixel_rain":
                frames = EffectAnimations._create_pixel_rain_frames(base_image, frame_count, width, height, pixel_size)
            elif animation_type == "wave_distortion":
                frames = EffectAnimations._create_wave_distortion_frames(base_image, frame_count, width, height)
            elif animation_type == "explode_reassemble":
                frames = EffectAnimations._create_explode_reassemble_frames(base_image, frame_count, width, height)
            elif animation_type == "split_merge":
                frames = EffectAnimations._create_split_merge_frames(base_image, frame_count, width, height)
            elif animation_type == "electric_shock":
                frames = EffectAnimations._create_electric_shock_frames(base_image, frame_count, width, height)
            elif animation_type == "rubberband":
                frames = EffectAnimations._create_rubberband_frames(base_image, frame_count, width, height)
            else:
                # デフォルト: heartbeat
                frames = EffectAnimations._create_heartbeat_frames(base_image, frame_count, width, height)
            
            # ピクセルアート処理を適用
            return EffectAnimations.apply_pixel_art_processing_to_frames(frames, pixel_size, palette_size)
            
        except Exception as e:
            logger.error(f"Effect animation creation failed: {str(e)}")
            return [base_image]  # エラー時は元画像を返す
    
    @staticmethod
    def _create_glitch_wave_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """グリッチウェーブフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            
            # グリッチパターン
            for y in range(0, height, 8):
                shift = int(8 * math.sin(2 * math.pi * (i / frame_count + y / height)))
                if random.random() > 0.7:  # ランダムグリッチ
                    shift += random.randint(-15, 15)
                
                if y < height:
                    pixels[y:min(y+8, height)] = np.roll(pixels[y:min(y+8, height)], shift, axis=1)
            
            frame = Image.fromarray(pixels.astype('uint8'))
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_heartbeat_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """ハートビートフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            t = i / frame_count
            
            # ハートビートパターン
            if t < 0.15:
                scale = 1 + 0.08 * (t / 0.15)
            elif t < 0.25:
                scale = 1.08 - 0.08 * ((t - 0.15) / 0.1)
            elif t < 0.35:
                scale = 1 + 0.12 * ((t - 0.25) / 0.1)
            elif t < 0.45:
                scale = 1.12 - 0.12 * ((t - 0.35) / 0.1)
            else:
                scale = 1
            
            # スケール適用
            new_size = (int(width * scale), int(height * scale))
            scaled = base_image.resize(new_size, Image.NEAREST)
            
            # 中央配置
            frame = EffectAnimations.create_safe_frame(base_image, width, height)
            x_offset = (width - new_size[0]) // 2
            y_offset = (height - new_size[1]) // 2
            frame.paste(scaled, (x_offset, y_offset))
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_spiral_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """スパイラルフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            t = i / frame_count
            angle = 360 * t * 2
            scale = 0.6 + 0.4 * math.sin(2 * math.pi * t)
            
            # 回転とスケール
            frame = base_image.copy()
            frame = EffectAnimations.apply_transform_safe(
                frame, 
                lambda img: img.rotate(angle, expand=False, fillcolor=(0, 0, 0))
            )
            
            new_size = (int(width * (0.7 + scale * 0.3)), int(height * (0.7 + scale * 0.3)))
            frame = frame.resize(new_size, Image.NEAREST)
            
            # 中央配置
            final_frame = EffectAnimations.create_safe_frame(base_image, width, height)
            x_offset = (width - new_size[0]) // 2
            y_offset = (height - new_size[1]) // 2
            final_frame.paste(frame, (x_offset, y_offset))
            
            frames.append(final_frame)
        
        return frames
    
    @staticmethod
    def _create_pixel_rain_frames(base_image: Image.Image, frame_count: int, width: int, height: int, pixel_size: int) -> List[Image.Image]:
        """ピクセルレインフレーム生成"""
        frames = []
        
        # ピクセル情報を収集
        pixels_data = []
        for y in range(0, height, pixel_size):
            for x in range(0, width, pixel_size):
                color = base_image.getpixel((min(x, width-1), min(y, height-1)))
                if sum(color) > 30:  # 暗すぎるピクセルは除外
                    pixels_data.append({
                        'x': x, 'y': y, 'color': color,
                        'fall_delay': random.uniform(0, 0.4),
                        'fall_speed': random.uniform(0.8, 2.0)
                    })
        
        for i in range(frame_count):
            frame = EffectAnimations.create_safe_frame(base_image, width, height)
            draw = ImageDraw.Draw(frame)
            t = i / frame_count
            
            for pixel in pixels_data:
                if t > pixel['fall_delay']:
                    fall_progress = (t - pixel['fall_delay']) / (1 - pixel['fall_delay'])
                    current_y = pixel['y'] - (pixel['y'] + height) * (1 - (1 - fall_progress) ** 2)
                    
                    if current_y >= -pixel_size:
                        draw.rectangle([
                            pixel['x'], int(current_y),
                            pixel['x'] + pixel_size, int(current_y) + pixel_size
                        ], fill=pixel['color'])
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_wave_distortion_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """波状歪みフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            new_pixels = np.zeros_like(pixels)
            
            for y in range(height):
                for x in range(width):
                    # 波の歪み計算
                    wave_x = x + int(6 * math.sin(2 * math.pi * (y / 25 + i / frame_count)))
                    wave_y = y + int(3 * math.sin(2 * math.pi * (x / 35 + i / frame_count)))
                    
                    # 境界チェック
                    wave_x = max(0, min(width - 1, wave_x))
                    wave_y = max(0, min(height - 1, wave_y))
                    
                    new_pixels[y, x] = pixels[wave_y, wave_x]
            
            frame = Image.fromarray(new_pixels.astype('uint8'))
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_explode_reassemble_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """爆発・再集合フレーム生成"""
        frames = []
        part_size = 24
        
        # パーツ分割
        parts = []
        for y in range(0, height, part_size):
            for x in range(0, width, part_size):
                part = base_image.crop((x, y, min(x + part_size, width), min(y + part_size, height)))
                parts.append({
                    'image': part, 'original_x': x, 'original_y': y,
                    'velocity_x': random.uniform(-25, 25),
                    'velocity_y': random.uniform(-30, -5),
                    'rotation': random.uniform(-30, 30)
                })
        
        for i in range(frame_count):
            frame = EffectAnimations.create_safe_frame(base_image, width, height)
            t = i / frame_count
            
            # イージング
            if t < 0.5:
                progress = t * 2
                ease_t = progress
            else:
                progress = (t - 0.5) * 2
                ease_t = 1 - EffectAnimations.create_ease_in_out(progress)
            
            for part in parts:
                x = part['original_x'] + part['velocity_x'] * ease_t
                y = part['original_y'] + part['velocity_y'] * ease_t + 9.8 * ease_t * ease_t * 8
                rotation = part['rotation'] * ease_t
                
                # パーツ配置
                try:
                    rotated_part = part['image'].rotate(rotation, expand=False)
                    frame.paste(rotated_part, (int(x), int(y)))
                except:
                    pass
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_split_merge_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """分裂・結合フレーム生成"""
        frames = []
        half_w, half_h = width // 2, height // 2
        
        parts = [
            base_image.crop((0, 0, half_w, half_h)),
            base_image.crop((half_w, 0, width, half_h)),
            base_image.crop((0, half_h, half_w, height)),
            base_image.crop((half_w, half_h, width, height))
        ]
        
        for i in range(frame_count):
            frame = EffectAnimations.create_safe_frame(base_image, width, height)
            t = i / frame_count
            
            if t < 0.5:
                progress = t * 2
                offsets = [(-15 * progress, -15 * progress), (15 * progress, -15 * progress),
                          (-15 * progress, 15 * progress), (15 * progress, 15 * progress)]
                rotation = 120 * progress
            else:
                progress = (t - 0.5) * 2
                ease_progress = EffectAnimations.create_ease_in_out(progress)
                offsets = [(-15 * (1 - ease_progress), -15 * (1 - ease_progress)),
                          (15 * (1 - ease_progress), -15 * (1 - ease_progress)),
                          (-15 * (1 - ease_progress), 15 * (1 - ease_progress)),
                          (15 * (1 - ease_progress), 15 * (1 - ease_progress))]
                rotation = 120 * (1 - ease_progress)
            
            positions = [(0, 0), (half_w, 0), (0, half_h), (half_w, half_h)]
            for idx, (part, offset, pos) in enumerate(zip(parts, offsets, positions)):
                try:
                    rotated = part.rotate(rotation * (1 if idx % 2 == 0 else -1), expand=False)
                    frame.paste(rotated, (int(pos[0] + offset[0]), int(pos[1] + offset[1])))
                except:
                    pass
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_electric_shock_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """電撃エフェクトフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            
            # 稲妻の生成
            if random.random() > 0.4:
                draw = ImageDraw.Draw(frame)
                
                # 稲妻のパス
                points = [(random.randint(0, width), 0)]
                y = 0
                while y < height:
                    y += random.randint(8, 20)
                    x = points[-1][0] + random.randint(-25, 25)
                    x = max(0, min(width, x))
                    points.append((x, min(y, height)))
                
                # 稲妻を描画
                for j in range(len(points) - 1):
                    draw.line([points[j], points[j+1]], fill=(255, 255, 150), width=random.randint(1, 3))
                
                # 画像を少し歪める
                if len(points) > 1:
                    pixels = np.array(frame)
                    for point in points:
                        px, py = point
                        if 0 <= py < height:
                            shift = random.randint(-5, 5)
                            pixels[py:min(py+5, height)] = np.roll(pixels[py:min(py+5, height)], shift, axis=1)
                    frame = Image.fromarray(pixels.astype('uint8'))
                
                # 明度を上げる
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(1.3)
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_rubberband_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """ラバーバンドフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            t = i / frame_count
            
            # ラバーバンド効果
            stretch_x = 1 + 0.25 * math.sin(2 * math.pi * t)
            stretch_y = 1 - 0.15 * math.sin(2 * math.pi * t)
            
            # スケール適用
            new_size = (int(width * stretch_x), int(height * stretch_y))
            frame = base_image.resize(new_size, Image.NEAREST)
            
            # 中央配置
            final_frame = EffectAnimations.create_safe_frame(base_image, width, height)
            x_offset = (width - new_size[0]) // 2
            y_offset = (height - new_size[1]) // 2
            final_frame.paste(frame, (x_offset, y_offset))
            
            frames.append(final_frame)
        
        return frames


# サポートされているエフェクトアニメーション種類
EFFECT_ANIMATION_TYPES = [
    'glitch_wave', 'heartbeat', 'spiral', 'pixel_rain', 'wave_distortion',
    'explode_reassemble', 'split_merge', 'electric_shock', 'rubberband'
]
