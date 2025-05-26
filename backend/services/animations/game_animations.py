"""
Pixa - ゲーム開発向けアニメーション
"""
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
from typing import List
import logging

from .animation_base import AnimationBase

logger = logging.getLogger(__name__)


class GameAnimations(AnimationBase):
    """ゲーム開発向けアニメーション生成クラス"""
    
    @staticmethod
    def create_frames(base_image: Image.Image,
                     animation_type: str,
                     frame_count: int = 8,
                     pixel_size: int = 8,
                     palette_size: int = 16,
                     **kwargs) -> List[Image.Image]:
        """ゲーム開発向けアニメーションフレーム生成"""
        
        # パラメータ検証
        params = GameAnimations.validate_parameters(base_image, frame_count, pixel_size, palette_size)
        width, height = params['width'], params['height']
        frame_count = params['frame_count']
        
        try:
            # アニメーション種類別の処理
            if animation_type == "walk_cycle":
                frames = GameAnimations._create_walk_cycle_frames(base_image, frame_count, width, height)
            elif animation_type == "idle_breathing":
                frames = GameAnimations._create_idle_breathing_frames(base_image, frame_count, width, height)
            elif animation_type == "attack_slash":
                frames = GameAnimations._create_attack_slash_frames(base_image, frame_count, width, height)
            elif animation_type == "jump_landing":
                frames = GameAnimations._create_jump_landing_frames(base_image, frame_count, width, height)
            elif animation_type == "walk_4direction":
                frames = GameAnimations._create_walk_4direction_frames(base_image, frame_count, width, height)
            elif animation_type == "damage_flash":
                frames = GameAnimations._create_damage_flash_frames(base_image, frame_count, width, height)
            else:
                # デフォルト: idle_breathing
                frames = GameAnimations._create_idle_breathing_frames(base_image, frame_count, width, height)
            
            # ピクセルアート処理を適用
            return GameAnimations.apply_pixel_art_processing_to_frames(frames, pixel_size, palette_size)
            
        except Exception as e:
            logger.error(f"Game animation creation failed: {str(e)}")
            return [base_image]  # エラー時は元画像を返す
    
    @staticmethod
    def _create_walk_cycle_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """歩行サイクルフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            
            # 歩行サイクル（2ステップ）
            cycle_phase = (i / frame_count * 2) % 2
            
            # 足の動き計算
            foot_offset = int(3 * math.sin(cycle_phase * math.pi))
            body_bob = int(1 * math.sin(cycle_phase * 2 * math.pi))
            
            # 下半身の動き（足）
            lower_body_start = int(height * 0.6)
            if lower_body_start < height:
                for y in range(lower_body_start, height):
                    if y < len(pixels):
                        # 左右の足を交互に
                        left_half = pixels[y, :width//2]
                        right_half = pixels[y, width//2:]
                        
                        if cycle_phase < 1:
                            # 左足前
                            left_half = np.roll(left_half, foot_offset, axis=0)
                            right_half = np.roll(right_half, -foot_offset//2, axis=0)
                        else:
                            # 右足前
                            left_half = np.roll(left_half, -foot_offset//2, axis=0)
                            right_half = np.roll(right_half, foot_offset, axis=0)
                        
                        pixels[y, :width//2] = left_half
                        pixels[y, width//2:] = right_half
            
            # 全体の上下動
            if body_bob != 0:
                pixels = np.roll(pixels, body_bob, axis=0)
            
            frame = Image.fromarray(pixels.astype('uint8'))
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_idle_breathing_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """アイドル（呼吸）フレーム生成"""
        frames = []
        
        for i in range(frame_count):
            # 呼吸による微細な変化
            breath_phase = i / frame_count
            breath_scale = 1.0 + 0.015 * math.sin(2 * math.pi * breath_phase)
            vertical_offset = int(1 * math.sin(2 * math.pi * breath_phase))
            
            # 微細リサイズ
            new_width = int(width * breath_scale)
            new_height = int(height * breath_scale)
            temp_frame = base_image.resize((new_width, new_height), Image.NEAREST)
            
            # 中央配置
            final_frame = GameAnimations.create_safe_frame(base_image, width, height)
            x_offset = (width - new_width) // 2
            y_offset = (height - new_height) // 2 + vertical_offset
            
            if x_offset >= 0 and y_offset >= 0:
                final_frame.paste(temp_frame, (x_offset, y_offset))
            else:
                final_frame = base_image.copy()
            
            frames.append(final_frame)
        
        return frames
    
    @staticmethod  
    def _create_attack_slash_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """攻撃（斬撃）フレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            t = i / frame_count
            
            # 3段階の攻撃モーション
            if t < 0.3:
                # 予備動作（後退）
                progress = t / 0.3
                offset_x = int(-6 * progress)
                rotation = -8 * progress
            elif t < 0.7:
                # 攻撃（前進）
                progress = (t - 0.3) / 0.4
                offset_x = int(12 * progress - 6)
                rotation = 12 * progress - 8
                
                # 攻撃エフェクト
                if progress > 0.5:
                    draw = ImageDraw.Draw(frame)
                    effect_alpha = int(255 * (1.0 - progress))
                    draw.line([(int(width * 0.7), int(height * 0.4)), 
                              (int(width * 0.9), int(height * 0.6))], 
                             fill=(255, 255, 200), width=2)
            else:
                # 戻り
                progress = (t - 0.7) / 0.3
                ease_progress = GameAnimations.create_ease_in_out(progress)
                offset_x = int(6 * (1 - ease_progress))
                rotation = 4 * (1 - ease_progress)
            
            # 変形適用
            if offset_x != 0:
                pixels = np.array(frame)
                pixels = np.roll(pixels, offset_x, axis=1)
                frame = Image.fromarray(pixels.astype('uint8'))
            
            if abs(rotation) > 0.1:
                frame = GameAnimations.apply_transform_safe(
                    frame,
                    lambda img: img.rotate(rotation, expand=False, fillcolor=(0, 0, 0))
                )
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_jump_landing_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """ジャンプ・着地フレーム生成"""
        frames = []
        
        for i in range(frame_count):
            t = i / frame_count
            
            # ジャンプフェーズの計算
            if t < 0.2:
                # しゃがみ
                progress = t / 0.2
                scale_y = 1.0 - 0.15 * progress
                scale_x = 1.0 + 0.08 * progress
                y_offset = int(height * 0.08 * progress)
            elif t < 0.5:
                # ジャンプ上昇
                progress = (t - 0.2) / 0.3
                scale_y = 0.85 + 0.25 * progress
                scale_x = 1.08 - 0.08 * progress
                y_offset = int(-height * 0.25 * progress)
            elif t < 0.8:
                # 空中滞空
                progress = (t - 0.5) / 0.3
                scale_y = 1.1 - 0.08 * progress
                scale_x = 1.0
                y_offset = int(-height * 0.25)
            else:
                # 着地
                progress = (t - 0.8) / 0.2
                ease_progress = GameAnimations.create_ease_bounce(progress)
                scale_y = 1.02 - 0.02 * ease_progress
                scale_x = 1.0 + 0.03 * (1 - ease_progress)
                y_offset = int(-height * 0.25 * (1 - ease_progress))
            
            # スケール適用
            new_width = max(int(width * scale_x), 1)
            new_height = max(int(height * scale_y), 1)
            
            try:
                scaled_frame = base_image.resize((new_width, new_height), Image.NEAREST)
                final_frame = GameAnimations.create_safe_frame(base_image, width, height)
                
                x_pos = (width - new_width) // 2
                y_pos = max(0, (height - new_height) + y_offset)
                
                final_frame.paste(scaled_frame, (x_pos, y_pos))
                frames.append(final_frame)
            except:
                frames.append(base_image.copy())
        
        return frames
    
    @staticmethod
    def _create_walk_4direction_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """4方向歩行フレーム生成"""
        frames = []
        frames_per_direction = max(frame_count // 4, 1)
        
        for i in range(frame_count):
            direction_index = i // frames_per_direction
            direction_frame = i % frames_per_direction
            
            frame = base_image.copy()
            
            # 方向別処理
            if direction_index % 4 == 0:  # 下
                pass  # そのまま
            elif direction_index % 4 == 1:  # 左
                frame = GameAnimations.apply_transform_safe(frame, lambda img: img.transpose(Image.FLIP_LEFT_RIGHT))
            elif direction_index % 4 == 2:  # 右
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(1.05)
            else:  # 上
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(0.95)
            
            # 歩行動作
            if frames_per_direction > 1:
                walk_phase = direction_frame / frames_per_direction
                foot_movement = int(2 * math.sin(walk_phase * 2 * math.pi))
                
                pixels = np.array(frame)
                lower_start = int(height * 0.6)
                for y in range(lower_start, min(height, len(pixels))):
                    pixels[y] = np.roll(pixels[y], foot_movement, axis=0)
                frame = Image.fromarray(pixels.astype('uint8'))
            
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_damage_flash_frames(base_image: Image.Image, frame_count: int, width: int, height: int) -> List[Image.Image]:
        """ダメージフラッシュフレーム生成"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            t = i / frame_count
            
            # 後退動作
            if t < 0.4:
                knockback_progress = t / 0.4
                x_offset = int(-8 * knockback_progress)
                
                pixels = np.array(frame)
                pixels = np.roll(pixels, x_offset, axis=1)
                frame = Image.fromarray(pixels.astype('uint8'))
            
            # フラッシュエフェクト
            if t < 0.6:
                flash_intensity = 1.0 - (t / 0.6)
                
                if flash_intensity > 0:
                    # 色調変更（赤みを加える）
                    enhancer = ImageEnhance.Color(frame)
                    frame = enhancer.enhance(0.7)
                    
                    # 赤フラッシュ
                    frame_array = np.array(frame)
                    flash_add = int(80 * flash_intensity)
                    frame_array[:, :, 0] = np.minimum(255, frame_array[:, :, 0] + flash_add)
                    frame = Image.fromarray(frame_array.astype('uint8'))
            
            frames.append(frame)
        
        return frames


# サポートされているゲームアニメーション種類
GAME_ANIMATION_TYPES = [
    'walk_cycle', 'idle_breathing', 'attack_slash', 
    'jump_landing', 'walk_4direction', 'damage_flash'
]
