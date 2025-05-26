"""
Pixa - 拡張アニメーション機能
より面白くて創造的な動きのパターン + GIF差分合成最適化
"""

import math
import random
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import numpy as np
import os

import math
import random
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import numpy as np
import os

def create_frame_difference(previous_frame, current_frame, tolerance=5):
    """
    フレーム間の差分を検出し、変更のない部分を透明にする
    
    Args:
        previous_frame: 前のフレーム（PIL Image）
        current_frame: 現在のフレーム（PIL Image）
        tolerance: 色の違いの許容値（0-255）
    
    Returns:
        透明化された差分フレーム（RGBA）
    """
    if previous_frame is None:
        # 最初のフレームはそのまま返す（RGBのまま）
        return current_frame.convert('RGB')
    
    # RGBに変換して比較
    prev_rgb = previous_frame.convert('RGB')
    curr_rgb = current_frame.convert('RGB')
    
    # numpy配列に変換
    prev_array = np.array(prev_rgb)
    curr_array = np.array(curr_rgb)
    
    # ピクセル単位での差分を計算
    diff = np.abs(prev_array.astype(int) - curr_array.astype(int))
    pixel_diff = np.max(diff, axis=2)  # RGB最大差分
    
    # 変化が小さいピクセルは前のフレームのピクセルを使用
    # これによりGIFの差分圧縮が効果的に機能する
    result_array = curr_array.copy()
    unchanged_mask = pixel_diff <= tolerance
    result_array[unchanged_mask] = prev_array[unchanged_mask]
    
    return Image.fromarray(result_array.astype('uint8'), 'RGB')

def optimize_gif_frames(frames, tolerance=3):
    """
    フレームリストを差分合成用に最適化
    より効果的な差分検出とフレーム最適化
    
    Args:
        frames: フレームのリスト
        tolerance: 差分検出の許容値（小さいほど厳密）
    
    Returns:
        最適化されたフレームリスト
    """
    if not frames:
        return []
    
    optimized_frames = []
    previous_frame = None
    
    for i, frame in enumerate(frames):
        # 全てRGBに統一
        frame_rgb = frame.convert('RGB')
        
        if i == 0:
            # 最初のフレームはそのまま
            optimized_frames.append(frame_rgb)
            previous_frame = frame_rgb
        else:
            # 差分フレームを生成（変化の少ない部分は前フレームと同じ色に）
            diff_frame = create_frame_difference(previous_frame, frame_rgb, tolerance)
            optimized_frames.append(diff_frame)
            previous_frame = frame_rgb
    
    return optimized_frames

def save_optimized_gif(frames, output_path, duration=100, loop=0, tolerance=3):
    """
    差分合成最適化されたGIFを保存
    
    Args:
        frames: フレームのリスト
        output_path: 出力パス
        duration: フレーム持続時間（ms）
        loop: ループ回数（0=無限）
        tolerance: 差分検出の許容値
    """
    if not frames:
        return
    
    # フレームを差分合成用に最適化
    optimized_frames = optimize_gif_frames(frames, tolerance)
    
    # より効果的なGIF保存オプション
    save_kwargs = {
        'save_all': True,
        'append_images': optimized_frames[1:],
        'duration': duration,
        'loop': loop,
        'optimize': True,  # 重要：ファイルサイズ最適化
        'disposal': 0,     # フレームを保持（差分に最適）
    }
    
    # パレット数を制限してファイルサイズを削減
    first_frame = optimized_frames[0]
    if hasattr(first_frame, 'quantize'):
        # 256色以下に制限
        first_frame = first_frame.quantize(colors=128, method=Image.MEDIANCUT, dither=0)
        optimized_frames = [first_frame] + [
            frame.quantize(colors=128, method=Image.MEDIANCUT, dither=0) 
            for frame in optimized_frames[1:]
        ]
        save_kwargs['palette'] = first_frame.getpalette()
    
    # GIFを保存
    optimized_frames[0].save(output_path, format='GIF', **save_kwargs)
    
    # ファイルサイズを表示
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"最適化されたGIFを保存: {output_path}")
        print(f"ファイルサイズ: {file_size:,} bytes ({file_size/1024:.1f} KB)")

def create_creative_animation_frames(base_image, animation_type, frame_count, pixel_size, palette_size):
    """
    より創造的なアニメーションフレームを生成
    """
    frames = []
    width, height = base_image.size
    
    if animation_type == "glitch_wave":
        # グリッチウェーブ - デジタル風の波打ちエフェクト
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
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "explode_reassemble":
        # 爆発して再集合 - パーツが飛び散って戻ってくる
        parts = []
        part_size = 32
        
        # 画像をパーツに分割
        for y in range(0, height, part_size):
            for x in range(0, width, part_size):
                part = base_image.crop((x, y, min(x + part_size, width), min(y + part_size, height)))
                parts.append({
                    'image': part,
                    'original_x': x,
                    'original_y': y,
                    'velocity_x': random.uniform(-30, 30),
                    'velocity_y': random.uniform(-40, -10),
                    'rotation': random.uniform(-45, 45)
                })
        
        for i in range(frame_count):
            frame = Image.new('RGB', base_image.size, (0, 0, 0))
            t = i / (frame_count - 1) if frame_count > 1 else 0
            
            # イージング関数（最初は速く、最後はゆっくり）
            ease_t = 1 - (1 - t) ** 3
            
            for part in parts:
                # 爆発→戻る動き
                if t < 0.5:
                    # 爆発フェーズ
                    progress = t * 2
                    x = part['original_x'] + part['velocity_x'] * progress
                    y = part['original_y'] + part['velocity_y'] * progress + 9.8 * progress * progress * 10
                    rotation = part['rotation'] * progress
                else:
                    # 戻るフェーズ
                    progress = (t - 0.5) * 2
                    ease_progress = 1 - (1 - progress) ** 3
                    x = part['original_x'] + part['velocity_x'] * (1 - ease_progress)
                    y = part['original_y'] + part['velocity_y'] * (1 - ease_progress) + 9.8 * (1 - ease_progress) * (1 - ease_progress) * 10
                    rotation = part['rotation'] * (1 - ease_progress)
                
                # パーツを回転して貼り付け
                rotated_part = part['image'].rotate(rotation, expand=False)
                frame.paste(rotated_part, (int(x), int(y)))
            
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "pixel_rain":
        # ピクセルレイン - ピクセルが雨のように落ちて再構築
        pixels_data = []
        
        # ピクセルデータを収集
        for y in range(0, height, pixel_size):
            for x in range(0, width, pixel_size):
                color = base_image.getpixel((min(x, width-1), min(y, height-1)))
                if color != (0, 0, 0):  # 黒以外のピクセル
                    pixels_data.append({
                        'x': x,
                        'y': y,
                        'color': color,
                        'fall_delay': random.uniform(0, 0.5),
                        'fall_speed': random.uniform(1, 3)
                    })
        
        for i in range(frame_count):
            frame = Image.new('RGB', base_image.size, (0, 0, 0))
            draw = ImageDraw.Draw(frame)
            t = i / (frame_count - 1) if frame_count > 1 else 0
            
            for pixel in pixels_data:
                # 落下アニメーション
                if t > pixel['fall_delay']:
                    fall_progress = (t - pixel['fall_delay']) / (1 - pixel['fall_delay'])
                    current_y = pixel['y'] * (1 - fall_progress) - height * fall_progress
                    current_y = pixel['y'] - (pixel['y'] + height) * (1 - (1 - fall_progress) ** 2)
                    
                    draw.rectangle([
                        pixel['x'], 
                        int(current_y), 
                        pixel['x'] + pixel_size, 
                        int(current_y) + pixel_size
                    ], fill=pixel['color'])
            
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "wave_distortion":
        # 波状歪み - 水面のような波打ち効果
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            new_pixels = np.zeros_like(pixels)
            
            for y in range(height):
                for x in range(width):
                    # 波の計算
                    wave_x = x + int(10 * math.sin(2 * math.pi * (y / 30 + i / frame_count)))
                    wave_y = y + int(5 * math.sin(2 * math.pi * (x / 40 + i / frame_count)))
                    
                    # 境界チェック
                    wave_x = max(0, min(width - 1, wave_x))
                    wave_y = max(0, min(height - 1, wave_y))
                    
                    new_pixels[y, x] = pixels[wave_y, wave_x]
            
            frame = Image.fromarray(new_pixels.astype('uint8'))
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "heartbeat":
        # ハートビート - 脈動するような拡大縮小
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
            
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "spiral":
        # スパイラル - 螺旋状に回転しながら拡大縮小
        for i in range(frame_count):
            t = i / frame_count
            angle = 360 * t * 2  # 2回転
            scale = 0.5 + 0.5 * math.sin(2 * math.pi * t)
            
            # 画像を変形
            frame = base_image.copy()
            frame = frame.rotate(angle, expand=False, fillcolor=(0, 0, 0))
            
            # スケール変更
            new_size = (int(width * (0.8 + scale * 0.4)), int(height * (0.8 + scale * 0.4)))
            frame = frame.resize(new_size, Image.NEAREST)
            
            # 中央に配置
            final_frame = Image.new('RGB', base_image.size, (0, 0, 0))
            x_offset = (width - new_size[0]) // 2
            y_offset = (height - new_size[1]) // 2
            final_frame.paste(frame, (x_offset, y_offset))
            
            frame = apply_pixel_art_processing(final_frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "split_merge":
        # 分裂と結合 - 画像が分裂して回転しながら戻る
        for i in range(frame_count):
            t = i / frame_count
            frame = Image.new('RGB', base_image.size, (0, 0, 0))
            
            # 4つに分割
            half_w, half_h = width // 2, height // 2
            parts = [
                base_image.crop((0, 0, half_w, half_h)),  # 左上
                base_image.crop((half_w, 0, width, half_h)),  # 右上
                base_image.crop((0, half_h, half_w, height)),  # 左下
                base_image.crop((half_w, half_h, width, height))  # 右下
            ]
            
            # 各パーツの動き
            if t < 0.5:
                # 分裂フェーズ
                progress = t * 2
                offsets = [
                    (-20 * progress, -20 * progress),  # 左上
                    (20 * progress, -20 * progress),   # 右上
                    (-20 * progress, 20 * progress),   # 左下
                    (20 * progress, 20 * progress)     # 右下
                ]
                rotation = 180 * progress
            else:
                # 結合フェーズ
                progress = (t - 0.5) * 2
                ease_progress = 1 - (1 - progress) ** 3
                offsets = [
                    (-20 * (1 - ease_progress), -20 * (1 - ease_progress)),
                    (20 * (1 - ease_progress), -20 * (1 - ease_progress)),
                    (-20 * (1 - ease_progress), 20 * (1 - ease_progress)),
                    (20 * (1 - ease_progress), 20 * (1 - ease_progress))
                ]
                rotation = 180 * (1 - ease_progress)
            
            # パーツを配置
            positions = [(0, 0), (half_w, 0), (0, half_h), (half_w, half_h)]
            for idx, (part, offset, pos) in enumerate(zip(parts, offsets, positions)):
                rotated = part.rotate(rotation * (1 if idx % 2 == 0 else -1), expand=False)
                frame.paste(rotated, (int(pos[0] + offset[0]), int(pos[1] + offset[1])))
            
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    elif animation_type == "electric_shock":
        # 電撃エフェクト - 稲妻のような歪み
        for i in range(frame_count):
            frame = base_image.copy()
            pixels = np.array(frame)
            
            # ランダムな稲妻パターン
            shock_lines = []
            if random.random() > 0.3:  # 70%の確率で稲妻発生
                start_x = random.randint(0, width)
                y = 0
                x = start_x
                while y < height:
                    shock_lines.append((x, y))
                    y += random.randint(5, 15)
                    x += random.randint(-20, 20)
                    x = max(0, min(width - 1, x))
            
            # 稲妻の影響で画像を歪める
            for x, y in shock_lines:
                # 稲妻の周辺をシフト
                for dy in range(-10, 10):
                    for dx in range(-10, 10):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            shift = int(5 * math.exp(-((dx**2 + dy**2) / 50)))
                            if nx + shift < width:
                                pixels[ny, nx] = pixels[ny, min(nx + shift, width - 1)]
            
            # 稲妻を描画
            frame = Image.fromarray(pixels.astype('uint8'))
            draw = ImageDraw.Draw(frame)
            for i in range(len(shock_lines) - 1):
                draw.line([shock_lines[i], shock_lines[i+1]], fill=(255, 255, 128), width=2)
            
            # 明度を瞬間的に上げる
            if shock_lines:
                enhancer = ImageEnhance.Brightness(frame)
                frame = enhancer.enhance(1.5)
            
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    else:  # デフォルトは"rubberband"
        # ラバーバンド - ゴムのように伸び縮み
        for i in range(frame_count):
            t = i / frame_count
            frame = base_image.copy()
            
            # 伸縮の計算
            stretch_x = 1 + 0.3 * math.sin(2 * math.pi * t)
            stretch_y = 1 - 0.2 * math.sin(2 * math.pi * t)
            
            # アスペクト比を変更
            new_size = (int(width * stretch_x), int(height * stretch_y))
            frame = frame.resize(new_size, Image.NEAREST)
            
            # 中央に配置
            final_frame = Image.new('RGB', base_image.size, (0, 0, 0))
            x_offset = (width - new_size[0]) // 2
            y_offset = (height - new_size[1]) // 2
            final_frame.paste(frame, (x_offset, y_offset))
            
            frame = apply_pixel_art_processing(final_frame, pixel_size, palette_size)
            frames.append(frame)
    
    return frames

def create_and_save_optimized_animation(base_image, animation_type, frame_count=16, pixel_size=8, palette_size=16, 
                                      output_path=None, duration=100, tolerance=10):
    """
    アニメーションフレームを生成し、差分合成最適化GIFとして保存
    
    Args:
        base_image: ベース画像
        animation_type: アニメーションタイプ
        frame_count: フレーム数
        pixel_size: ピクセルサイズ
        palette_size: パレットサイズ
        output_path: 出力パス（Noneの場合は自動生成）
        duration: フレーム持続時間（ms）
        tolerance: 差分検出の許容値
    
    Returns:
        tuple: (フレームリスト, 最適化されたGIFパス)
    """
    # 通常のフレーム生成
    frames = create_creative_animation_frames(base_image, animation_type, frame_count, pixel_size, palette_size)
    
    # 出力パスの自動生成
    if output_path is None:
        output_path = f"optimized_animation_{animation_type}.gif"
    
    # 差分合成最適化GIFとして保存
    save_optimized_gif(frames, output_path, duration, loop=0, tolerance=tolerance)
    
    return frames, output_path

def batch_create_optimized_animations(base_image, output_dir="./", pixel_size=8, palette_size=16):
    """
    全種類のアニメーションを差分合成最適化GIFとして一括生成
    
    Args:
        base_image: ベース画像
        output_dir: 出力ディレクトリ
        pixel_size: ピクセルサイズ
        palette_size: パレットサイズ
    
    Returns:
        dict: アニメーションタイプ別のファイルパス
    """
    animation_types = [
        "glitch_wave", "explode_reassemble", "pixel_rain", "wave_distortion",
        "heartbeat", "spiral", "split_merge", "electric_shock", "rubberband"
    ]
    
    results = {}
    
    for anim_type in animation_types:
        output_path = os.path.join(output_dir, f"optimized_{anim_type}.gif")
        
        try:
            frames, saved_path = create_and_save_optimized_animation(
                base_image=base_image,
                animation_type=anim_type,
                frame_count=16,
                pixel_size=pixel_size,
                palette_size=palette_size,
                output_path=output_path,
                duration=100,
                tolerance=10
            )
            
            results[anim_type] = {
                'path': saved_path,
                'frame_count': len(frames),
                'success': True
            }
            print(f"✓ {anim_type}: {saved_path}")
            
        except Exception as e:
            results[anim_type] = {
                'path': None,
                'error': str(e),
                'success': False
            }
            print(f"✗ {anim_type}: エラー - {e}")
    
    return results


# 既存のapply_pixel_art_processing関数のインポートが必要
def apply_pixel_art_processing(image, pixel_size=8, palette_size=16):
    """ピクセルアート風後処理"""
    if image is None:
        return None
        
    original_size = image.size
    
    # ピクセルサイズに基づいて縮小
    small_size = (
        max(original_size[0] // pixel_size, 16),
        max(original_size[1] // pixel_size, 16)
    )
    
    # 縮小（NEAREST で鮮明なピクセルエッジを保持）
    image_small = image.resize(small_size, Image.NEAREST)
    
    # カラーパレット制限
    if palette_size < 256:
        # より良い色選択のためにMEDIANCUTを使用
        image_small = image_small.quantize(colors=palette_size, method=Image.MEDIANCUT, dither=0)
        image_small = image_small.convert('RGB')
    
    # 元のサイズに拡大
    pixel_art = image_small.resize(original_size, Image.NEAREST)
    
    return pixel_art
