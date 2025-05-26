"""
Pixa - 画像処理ユーティリティ
"""
import base64
import io
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


def apply_pixel_art_processing(image: Image.Image, 
                             pixel_size: int = 8, 
                             palette_size: int = 16) -> Optional[Image.Image]:
    """ピクセルアート風後処理"""
    if image is None:
        return None
    
    try:
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
    
    except Exception as e:
        logger.error(f"Pixel art processing failed: {str(e)}")
        return image


def image_to_base64(image: Image.Image, format: str = 'PNG') -> Optional[str]:
    """画像をBase64エンコード"""
    if image is None:
        return None
    
    try:
        buffer = io.BytesIO()
        image.save(buffer, format=format, optimize=True)
        buffer.seek(0)
        
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f'data:image/{format.lower()};base64,{base64_str}'
    
    except Exception as e:
        logger.error(f"Base64 encoding failed: {str(e)}")
        return None


def base64_to_image(base64_str: str) -> Optional[Image.Image]:
    """Base64文字列を画像に変換"""
    try:
        # データURLプレフィックスを除去
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        image_bytes = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        return image
    
    except Exception as e:
        logger.error(f"Base64 decoding failed: {str(e)}")
        return None


def validate_image_size(image: Image.Image, 
                       max_size: int = 1024, 
                       min_size: int = 256) -> Image.Image:
    """画像サイズを検証・調整"""
    width, height = image.size
    
    # 最大サイズチェック
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    
    # 最小サイズチェック
    if width < min_size or height < min_size:
        ratio = max(min_size / width, min_size / height)
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    
    return image


def create_image_grid(images: List[Image.Image], 
                     cols: int = 3, 
                     padding: int = 10) -> Optional[Image.Image]:
    """画像のグリッドを作成"""
    if not images:
        return None
    
    try:
        # グリッドサイズ計算
        rows = (len(images) + cols - 1) // cols
        img_width, img_height = images[0].size
        
        grid_width = cols * img_width + (cols - 1) * padding
        grid_height = rows * img_height + (rows - 1) * padding
        
        # グリッド画像作成
        grid = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            
            x = col * (img_width + padding)
            y = row * (img_height + padding)
            
            grid.paste(img, (x, y))
        
        return grid
    
    except Exception as e:
        logger.error(f"Grid creation failed: {str(e)}")
        return None


def enhance_image(image: Image.Image, 
                 brightness: float = 1.0,
                 contrast: float = 1.0,
                 saturation: float = 1.0,
                 sharpness: float = 1.0) -> Image.Image:
    """画像の色調補正"""
    try:
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)
        
        return image
    
    except Exception as e:
        logger.error(f"Image enhancement failed: {str(e)}")
        return image


def get_image_info(image: Image.Image) -> dict:
    """画像情報を取得"""
    if image is None:
        return {}
    
    try:
        return {
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'size_mb': len(image.tobytes()) / (1024 * 1024)
        }
    
    except Exception as e:
        logger.error(f"Getting image info failed: {str(e)}")
        return {}
