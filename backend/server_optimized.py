#!/usr/bin/env python3
"""
Pixa - 最適化版サーバー実装
メモリ使用量と起動時間を大幅に削減
"""
import os
import sys
import gc
import torch

# 最適化1: 遅延インポート
def lazy_import():
    """必要な時だけインポートする"""
    global Image, ImageFilter, ImageEnhance
    global StableDiffusionPipeline, DiffusionPipeline
    global Flask, request, jsonify, CORS
    
    from PIL import Image, ImageFilter, ImageEnhance
    from diffusers import StableDiffusionPipeline, DiffusionPipeline
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
# 最適化2: メモリ効率的な設定
OPTIMIZATION_CONFIG = {
    'enable_attention_slicing': True,
    'enable_vae_slicing': True,
    'enable_sequential_cpu_offload': False,  # M2 Proでは不要
    'enable_model_cpu_offload': False,       # M2 Proでは不要
    'use_torch_compile': True,               # PyTorch 2.0+の最適化
    'use_channels_last': True,               # メモリレイアウト最適化
    'enable_xformers': True,                 # 可能な場合有効化
}

# 最適化3: スレッド数の最適化
def optimize_torch_threads():
    """M2 Pro用にスレッド数を最適化"""
    # M2 Proは10コアCPU（6性能 + 4効率）
    performance_cores = 6
    torch.set_num_threads(performance_cores)
    os.environ['OMP_NUM_THREADS'] = str(performance_cores)
    os.environ['MKL_NUM_THREADS'] = str(performance_cores)
    
# 最適化4: MPS最適化設定
def optimize_mps_settings():
    """Apple Silicon MPS用の最適化設定"""
    if torch.backends.mps.is_available():
        # MPSの最適化設定
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        torch.mps.set_per_process_memory_fraction(0.75)  # メモリ使用量制限
        
# 最適化5: パイプライン最適化
class OptimizedPipeline:
    def __init__(self, model_id):
        self.model_id = model_id
        self.pipeline = None
        self.device = None
        self.dtype = None
        
    def load(self):
        """最適化されたモデル読み込み"""
        # デバイス設定
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            self.dtype = torch.float16  # MPS最適化: float16使用
        else:
            self.device = torch.device("cpu")
            self.dtype = torch.float32
            
        # パイプライン読み込み
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=self.dtype,
            safety_checker=None,
            requires_safety_checker=False,
            use_safetensors=True,
            variant="fp16" if self.dtype == torch.float16 else None
        )
        
        # デバイスに転送
        self.pipeline = self.pipeline.to(self.device)
        
        # 最適化を適用
        self._apply_optimizations()
        
    def _apply_optimizations(self):
        """各種最適化を適用"""
        if OPTIMIZATION_CONFIG['enable_attention_slicing']:
            self.pipeline.enable_attention_slicing(slice_size=1)
            
        if OPTIMIZATION_CONFIG['enable_vae_slicing']:
            self.pipeline.enable_vae_slicing()
            
        if OPTIMIZATION_CONFIG['enable_xformers']:
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
                print("✅ xFormers有効化成功")
            except:
                print("⚠️ xFormers利用不可")
                
        if OPTIMIZATION_CONFIG['use_channels_last']:
            # メモリレイアウト最適化
            self.pipeline.unet = self.pipeline.unet.to(memory_format=torch.channels_last)
            self.pipeline.vae = self.pipeline.vae.to(memory_format=torch.channels_last)
            
        if OPTIMIZATION_CONFIG['use_torch_compile'] and hasattr(torch, 'compile'):
            # PyTorch 2.0+の最適化
            self.pipeline.unet = torch.compile(self.pipeline.unet, mode="reduce-overhead")
            print("✅ torch.compile有効化成功")
            
    def generate(self, **kwargs):
        """最適化された画像生成"""
        with torch.inference_mode():  # no_gradより高速
            with torch.autocast("mps" if self.device.type == "mps" else "cpu"):
                return self.pipeline(**kwargs)
                
# 最適化6: 画像処理の高速化
def optimized_pixel_art_processing(image, pixel_size=8, palette_size=16):
    """最適化されたピクセルアート処理"""
    import cv2
    import numpy as np
    
    # PILからnumpyへ変換
    img_array = np.array(image)
    
    # OpenCVで高速リサイズ
    height, width = img_array.shape[:2]
    small_height = height // pixel_size
    small_width = width // pixel_size
    
    # 縮小（INTER_NEAREST）
    small_img = cv2.resize(img_array, (small_width, small_height), interpolation=cv2.INTER_NEAREST)
    
    # カラー量子化（K-means）
    if palette_size < 256:
        # Reshape for k-means
        pixels = small_img.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, palette_size, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        
        # 再構築
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        quantized = quantized.reshape(small_img.shape)
        small_img = quantized
    
    # 拡大
    pixel_art = cv2.resize(small_img, (width, height), interpolation=cv2.INTER_NEAREST)
    
    # PILに戻す
    return Image.fromarray(pixel_art)

# 最適化7: メモリ管理
class MemoryManager:
    @staticmethod
    def cleanup():
        """積極的なメモリクリーンアップ"""
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    @staticmethod
    def log_memory_usage():
        """メモリ使用量をログ出力"""
        import psutil
        process = psutil.Process()
        mem_info = process.memory_info()
        print(f"メモリ使用量: RSS={mem_info.rss/1024/1024:.1f}MB")

# メイン初期化
if __name__ == "__main__":
    print("🚀 Pixa最適化版サーバー起動中...")
    
    # 最適化設定
    optimize_torch_threads()
    optimize_mps_settings()
    
    # 遅延インポート
    lazy_import()
    
    print("✅ 最適化設定完了")
