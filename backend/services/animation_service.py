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
            if animation_type == "walk_cycle":
                frames = AnimationService._create_walk_cycle_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "idle_breathing":
                frames = AnimationService._create_idle_breathing_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "attack_slash":
                frames = AnimationService._create_attack_slash_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "jump_landing":
                frames = AnimationService._create_jump_landing_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "walk_4direction":
                frames = AnimationService._create_walk_4direction_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "damage_flash":
                frames = AnimationService._create_damage_flash_frames(
                    base_image, frame_count, width, height
                )
            elif animation_type == "glitch_wave":
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
    
    @staticmethod
    def _create_walk_cycle_frames(base_image: Image.Image,
                                frame_count: int,
                                width: int,
                                height: int) -> List[Image.Image]:
        """歩行サイクルフレーム生成 - 左右の足を交互に動かす"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            
            # 歩行サイクルのフェーズ（0-1の範囲）
            cycle_phase = (i / frame_count * 2) % 2  # 2ステップサイクル
            
            # 足の動きの計算
            if cycle_phase < 0.5:
                # 左足前、右足後ろ
                left_foot_offset = int(2 * math.sin(cycle_phase * 2 * math.pi))
                right_foot_offset = -left_foot_offset
            elif cycle_phase < 1.0:
                # 両足中央
                left_foot_offset = 0
                right_foot_offset = 0
            elif cycle_phase < 1.5:
                # 右足前、左足後ろ
                right_foot_offset = int(2 * math.sin((cycle_phase - 1) * 2 * math.pi))
                left_foot_offset = -right_foot_offset
            else:
                # 両足中央
                left_foot_offset = 0
                right_foot_offset = 0
            
            # 上下の微動（歩行時の体の動き）
            body_bob = int(1 * math.sin(cycle_phase * 2 * math.pi))
            
            # 下半身を微調整（足の動きをシミュレート）
            lower_body_start = int(height * 0.6)  # 下半身の開始位置
            for y in range(lower_body_start, height):
                # 左半分と右半分で異なる動き
                left_side = pixels[y, :width//2]
                right_side = pixels[y, width//2:]
                
                # 左足の動き
                if left_foot_offset != 0:
                    left_side = np.roll(left_side, left_foot_offset, axis=0)
                
                # 右足の動き
                if right_foot_offset != 0:
                    right_side = np.roll(right_side, right_foot_offset, axis=0)
                
                pixels[y, :width//2] = left_side
                pixels[y, width//2:] = right_side
            
            # 全体を上下に微動
            if body_bob != 0:
                pixels = np.roll(pixels, body_bob, axis=0)
            
            frame = Image.fromarray(pixels.astype('uint8'))
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_idle_breathing_frames(base_image: Image.Image,
                                    frame_count: int,
                                    width: int,
                                    height: int) -> List[Image.Image]:
        """アイドル（呼吸）フレーム生成 - 微細な上下動と輪郭の微変化"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            
            # 呼吸サイクル（ゆっくりとした拡縮）
            breath_phase = i / frame_count
            breath_scale = 1.0 + 0.02 * math.sin(2 * math.pi * breath_phase)  # 2%の変化
            
            # 微細な上下動
            vertical_offset = int(1 * math.sin(2 * math.pi * breath_phase))
            
            # 呼吸による微細な拡縮
            new_width = int(width * breath_scale)
            new_height = int(height * breath_scale)
            
            # 微細リサイズ
            temp_frame = frame.resize((new_width, new_height), Image.NEAREST)
            
            # 元のサイズに戻しつつ中央配置
            final_frame = Image.new('RGB', (width, height), (0, 0, 0))
            x_offset = (width - new_width) // 2
            y_offset = (height - new_height) // 2 + vertical_offset
            
            final_frame.paste(temp_frame, (x_offset, y_offset))
            frames.append(final_frame)
        
        return frames
    
    @staticmethod
    def _create_attack_slash_frames(base_image: Image.Image,
                                  frame_count: int,
                                  width: int,
                                  height: int) -> List[Image.Image]:
        """攻撃（斬撃）フレーム生成 - 予備動作→攻撃→戻り"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            t = i / frame_count
            
            if t < 0.3:
                # 予備動作（後ろに引く）
                offset_x = int(-5 * (t / 0.3))
                offset_y = int(-2 * (t / 0.3))
                rotation = -10 * (t / 0.3)
            elif t < 0.6:
                # 攻撃動作（前に突進）
                attack_progress = (t - 0.3) / 0.3
                offset_x = int(15 * attack_progress - 5)
                offset_y = int(3 * attack_progress - 2)
                rotation = 15 * attack_progress - 10
                
                # 攻撃エフェクト（光る線）
                if attack_progress > 0.5:
                    draw = ImageDraw.Draw(frame)
                    start_x = int(width * 0.7)
                    start_y = int(height * 0.4)
                    end_x = int(width * 0.9)
                    end_y = int(height * 0.6)
                    draw.line([(start_x, start_y), (end_x, end_y)], 
                             fill=(255, 255, 200), width=2)
            else:
                # 戻り動作
                return_progress = (t - 0.6) / 0.4
                offset_x = int(10 * (1 - return_progress))
                offset_y = int(1 * (1 - return_progress))
                rotation = 5 * (1 - return_progress)
            
            # 画像を移動・回転
            if offset_x != 0 or offset_y != 0:
                pixels = np.roll(pixels, offset_x, axis=1)
                pixels = np.roll(pixels, offset_y, axis=0)
            
            if rotation != 0:
                frame = Image.fromarray(pixels.astype('uint8'))
                frame = frame.rotate(rotation, expand=False, fillcolor=(0, 0, 0))
                pixels = np.array(frame)
            
            frame = Image.fromarray(pixels.astype('uint8'))
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def _create_jump_landing_frames(base_image: Image.Image,
                                  frame_count: int,
                                  width: int,
                                  height: int) -> List[Image.Image]:
        """ジャンプ・着地フレーム生成 - 予備動作→ジャンプ→着地"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            t = i / frame_count
            
            if t < 0.2:
                # しゃがみ予備動作
                squat_progress = t / 0.2
                scale_y = 1.0 - 0.2 * squat_progress
                scale_x = 1.0 + 0.1 * squat_progress
                y_offset = int(height * 0.1 * squat_progress)
            elif t < 0.4:
                # ジャンプ上昇
                jump_progress = (t - 0.2) / 0.2
                scale_y = 0.8 + 0.3 * jump_progress
                scale_x = 1.1 - 0.1 * jump_progress
                y_offset = int(-height * 0.3 * jump_progress)
            elif t < 0.7:
                # 空中（最高点）
                air_progress = (t - 0.4) / 0.3
                scale_y = 1.1 - 0.1 * air_progress
                scale_x = 1.0
                y_offset = int(-height * 0.3)
            else:
                # 着地
                land_progress = (t - 0.7) / 0.3
                scale_y = 1.0 - 0.1 * (1 - land_progress)
                scale_x = 1.0 + 0.05 * (1 - land_progress)
                y_offset = int(-height * 0.3 * (1 - land_progress))
            
            # スケール変更
            new_width = int(width * scale_x)
            new_height = int(height * scale_y)
            scaled_frame = frame.resize((new_width, new_height), Image.NEAREST)
            
            # 位置調整
            final_frame = Image.new('RGB', (width, height), (0, 0, 0))
            x_pos = (width - new_width) // 2
            y_pos = (height - new_height) + y_offset
            
            final_frame.paste(scaled_frame, (x_pos, y_pos))
            frames.append(final_frame)
        
        return frames
    
    @staticmethod
    def _create_damage_flash_frames(base_image: Image.Image,
                                  frame_count: int,
                                  width: int,
                                  height: int) -> List[Image.Image]:
        """ダメージフラッシュフレーム生成 - 点滅と後退"""
        frames = []
        
        for i in range(frame_count):
            frame = base_image.copy()
            t = i / frame_count
            
            # 後退動作
            if t < 0.3:
                knockback_progress = t / 0.3
                x_offset = int(-10 * knockback_progress)
                frame_array = np.array(frame)
                frame_array = np.roll(frame_array, x_offset, axis=1)
                frame = Image.fromarray(frame_array.astype('uint8'))
            
            # フラッシュエフェクト（赤く点滅）
            flash_intensity = 0
            if t < 0.5:
                flash_intensity = 1.0 - (t / 0.5)
            
            if flash_intensity > 0:
                enhancer = ImageEnhance.Color(frame)
                frame = enhancer.enhance(0.5)  # 彩度を下げる
                
                # 赤みを加える
                frame_array = np.array(frame)
                frame_array[:, :, 0] = np.minimum(255, 
                    frame_array[:, :, 0] + int(100 * flash_intensity))
                frame = Image.fromarray(frame_array.astype('uint8'))
            
            frames.append(frame)
        
        return frames
    
    @staticmethod  
    def _create_walk_4direction_frames(base_image: Image.Image,
                                     frame_count: int,
                                     width: int,
                                     height: int) -> List[Image.Image]:
        """4方向歩行フレーム生成 - 上下左右の歩行サイクル"""
        frames = []
        directions = ['down', 'left', 'right', 'up']  # 4方向
        frames_per_direction = max(frame_count // 4, 2)
        
        for i in range(frame_count):
            direction_index = i // frames_per_direction
            direction_frame = i % frames_per_direction
            direction = directions[direction_index % 4]
            
            frame = base_image.copy()
            pixels = np.array(frame)
            
            # 歩行サイクル
            walk_phase = direction_frame / max(frames_per_direction, 1)
            foot_offset = int(2 * math.sin(walk_phase * 2 * math.pi))
            
            if direction == 'up':
                # 上向き歩行（少し暗く）
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(0.9)
                pixels = np.array(frame)
            elif direction == 'left':
                # 左向き歩行
                pixels = np.fliplr(pixels)  # 左右反転
            elif direction == 'right':
                # 右向き歩行（明るく）
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(1.1)
                pixels = np.array(frame)
            # down（正面）はそのまま
            
            # 足の動き
            lower_body_start = int(height * 0.6)
            for y in range(lower_body_start, height):
                if y < len(pixels):
                    pixels[y] = np.roll(pixels[y], foot_offset, axis=0)
            
            frame = Image.fromarray(pixels.astype('uint8'))
            frames.append(frame)
        
        return frames


# グローバルサービスインスタンス
animation_service = AnimationService()
