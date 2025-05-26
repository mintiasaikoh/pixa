"""
Pixa - アプリケーション設定
"""
import os
import torch
from typing import Dict, Any


class Config:
    """アプリケーション設定クラス"""
    
    # サーバー設定
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = False
    
    # AI モデル設定
    DEFAULT_MODEL_ID = "runwayml/stable-diffusion-v1-5"
    MAX_IMAGE_SIZE = 1024
    MIN_IMAGE_SIZE = 256
    DEFAULT_IMAGE_SIZE = 512
    
    # ピクセルアート設定
    DEFAULT_PIXEL_SIZE = 8
    MAX_PIXEL_SIZE = 20
    MIN_PIXEL_SIZE = 2
    DEFAULT_PALETTE_SIZE = 16
    MAX_PALETTE_SIZE = 64
    MIN_PALETTE_SIZE = 4
    
    # アニメーション設定
    DEFAULT_FRAME_COUNT = 8
    MAX_FRAME_COUNT = 20
    MIN_FRAME_COUNT = 2
    DEFAULT_FPS = 10
    MAX_FPS = 30
    MIN_FPS = 5
    
    # 差分合成最適化設定
    DEFAULT_TOLERANCE = 3
    MAX_TOLERANCE = 20
    MIN_TOLERANCE = 1
    DEFAULT_DURATION = 100
    MAX_DURATION = 1000
    MIN_DURATION = 50
    
    # M2 Pro最適化設定
    ENABLE_OPTIMIZATIONS = True
    MPS_MEMORY_FRACTION = 0.75
    CPU_THREADS = 6
    
    # ファイル設定
    MAX_FILE_SIZE_MB = 10
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    TEMP_DIR = './temp'
    
    @classmethod
    def get_device(cls) -> torch.device:
        """最適なデバイスを取得"""
        if torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")
    
    @classmethod
    def get_dtype(cls, device: torch.device) -> torch.dtype:
        """デバイスに適したデータ型を取得"""
        if device == torch.device("mps") or device == torch.device("cpu"):
            return torch.float32
        else:
            return torch.float16
    
    @classmethod
    def setup_optimizations(cls):
        """M2 Pro用最適化設定"""
        if cls.ENABLE_OPTIMIZATIONS:
            torch.set_num_threads(cls.CPU_THREADS)
            if torch.backends.mps.is_available():
                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                try:
                    torch.mps.set_per_process_memory_fraction(cls.MPS_MEMORY_FRACTION)
                except:
                    pass  # 古いPyTorchバージョンでは利用不可
    
    @classmethod 
    def validate_image_params(cls, width: int, height: int, pixel_size: int, palette_size: int) -> Dict[str, Any]:
        """画像パラメータの検証と正規化"""
        return {
            'width': max(min(width, cls.MAX_IMAGE_SIZE), cls.MIN_IMAGE_SIZE),
            'height': max(min(height, cls.MAX_IMAGE_SIZE), cls.MIN_IMAGE_SIZE),
            'pixel_size': max(min(pixel_size, cls.MAX_PIXEL_SIZE), cls.MIN_PIXEL_SIZE),
            'palette_size': max(min(palette_size, cls.MAX_PALETTE_SIZE), cls.MIN_PALETTE_SIZE)
        }
    
    @classmethod
    def validate_animation_params(cls, frame_count: int, fps: int) -> Dict[str, Any]:
        """アニメーションパラメータの検証と正規化"""
        return {
            'frame_count': max(min(frame_count, cls.MAX_FRAME_COUNT), cls.MIN_FRAME_COUNT),
            'fps': max(min(fps, cls.MAX_FPS), cls.MIN_FPS)
        }
    
    @classmethod
    def validate_optimization_params(cls, tolerance: int, duration: int) -> Dict[str, Any]:
        """最適化パラメータの検証と正規化"""
        return {
            'tolerance': max(min(tolerance, cls.MAX_TOLERANCE), cls.MIN_TOLERANCE),
            'duration': max(min(duration, cls.MAX_DURATION), cls.MIN_DURATION)
        }


# サポートされているアニメーションタイプ
ANIMATION_TYPES = [
    'glitch_wave', 'explode_reassemble', 'pixel_rain', 'wave_distortion',
    'heartbeat', 'spiral', 'split_merge', 'electric_shock', 'rubberband'
]

# デバッグ用設定
class DevConfig(Config):
    DEBUG = True
    HOST = '127.0.0.1'

# 本番用設定
class ProdConfig(Config):
    DEBUG = False
    ENABLE_OPTIMIZATIONS = True
