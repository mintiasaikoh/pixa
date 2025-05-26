#!/usr/bin/env python3
"""
Pixa - AIピクセルアート生成アプリケーション
M2 Pro最適化 Flaskバックエンドサーバー（改善版）
バグ修正とパフォーマンス最適化を含む
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline, DiffusionPipeline, UNet2DConditionModel, LCMScheduler
from diffusers.loaders import FromSingleFileMixin
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io
import base64
import os
import logging
from datetime import datetime
import re
import imageio
import math
import gc  # メモリ管理
import random
from glitch_art_generator import GlitchArtGenerator
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)  # RuntimeWarningを抑制

# M2 Pro用最適化設定
ENABLE_OPTIMIZATIONS = True
if ENABLE_OPTIMIZATIONS:
    torch.set_num_threads(6)  # M2 Proの性能コア数
    if torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        try:
            torch.mps.set_per_process_memory_fraction(0.75)
        except:
            pass

try:
    from model_configs import enhance_prompt_for_model, enhance_negative_prompt_for_model
except ImportError:
    def enhance_prompt_for_model(prompt, model_id, context=None):
        if "pixel art" not in prompt.lower():
            return f"{prompt}, pixel art style, 8-bit, retro game sprite"
        return prompt
    
    def enhance_negative_prompt_for_model(negative_prompt, model_id):
        return negative_prompt

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask アプリケーション
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# グローバル変数
pipeline = None
current_model_id = None
device = None
model_configs_cache = {}

def get_optimal_device():
    """最適なデバイスを選択"""
    global device
    if device:
        return device
        
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        logger.info("Using Metal Performance Shaders (MPS) for Apple Silicon")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info("Using CUDA GPU")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU")
    return device

def cleanup_memory():
    """メモリクリーンアップ（最適化）"""
    gc.collect()
    if device and device.type == "mps":
        torch.mps.empty_cache()
    elif device and device.type == "cuda":
        torch.cuda.empty_cache()

def safe_image_generation(pipeline, prompt, negative_prompt, **kwargs):
    """
    安全な画像生成（真っ黒な画像を防ぐ）
    """
    try:
        # 最初の生成試行
        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            **kwargs
        )
        
        image = result.images[0]
        image_array = np.array(image)
        
        # 画像が真っ黒かチェック
        if image_array.max() == 0 or image_array.mean() < 1:
            logger.warning("Detected black image, attempting recovery...")
            
            # リトライ：ガイダンススケールを調整
            kwargs['guidance_scale'] = max(5.0, kwargs.get('guidance_scale', 7.5) * 0.8)
            kwargs['num_inference_steps'] = max(20, kwargs.get('num_inference_steps', 30))
            
            # VAE関連の設定をリセット
            if hasattr(pipeline, 'vae'):
                pipeline.vae.enable_slicing()
                pipeline.vae.enable_tiling()
            
            result = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                **kwargs
            )
            image = result.images[0]
            
        return image
        
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise

def initialize_pipeline(model_id="runwayml/stable-diffusion-v1-5", force_reload=False):
    """パイプラインの初期化（最適化版）"""
    global pipeline, current_model_id, device
    
    try:
        if current_model_id == model_id and not force_reload:
            logger.info(f"Using cached pipeline for {model_id}")
            return True
            
        # メモリクリーンアップ
        if pipeline:
            del pipeline
            cleanup_memory()
        
        device = get_optimal_device()
        logger.info(f"Loading model: {model_id}")
        
        # パイプライン設定
        pipeline_kwargs = {
            "torch_dtype": torch.float32 if device.type == "mps" else torch.float16,
            "use_safetensors": True,
            "safety_checker": None,
            "requires_safety_checker": False
        }
        
        # モデルタイプに応じた読み込み
        if "xl" in model_id.lower():
            pipeline = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                **pipeline_kwargs
            )
        else:
            pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                **pipeline_kwargs
            )
        
        pipeline = pipeline.to(device)
        
        # 最適化設定
        if ENABLE_OPTIMIZATIONS:
            # Attention Slicing
            pipeline.enable_attention_slicing(slice_size=1)
            
            # VAE最適化
            if hasattr(pipeline, 'vae'):
                pipeline.vae.enable_slicing()
                pipeline.vae.enable_tiling()
            
            # xFormersの有効化（利用可能な場合）
            try:
                pipeline.enable_xformers_memory_efficient_attention()
                logger.info("xFormers enabled for memory efficiency")
            except:
                logger.info("xFormers not available, using standard attention")
            
            # Channels Last メモリフォーマット（PyTorch 2.0+）
            if hasattr(torch, 'channels_last'):
                pipeline.unet = pipeline.unet.to(memory_format=torch.channels_last)
                if hasattr(pipeline, 'vae'):
                    pipeline.vae = pipeline.vae.to(memory_format=torch.channels_last)
        
        current_model_id = model_id
        logger.info(f"Pipeline initialized successfully for {model_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

def apply_pixel_art_processing(image, pixel_size=8, palette_size=16):
    """ピクセルアート風後処理（改善版）"""
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
    
    # コントラスト強調（オプション）
    enhancer = ImageEnhance.Contrast(pixel_art)
    pixel_art = enhancer.enhance(1.2)
    
    return pixel_art

@app.route('/')
def index():
    """メインページ"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': pipeline is not None,
        'current_model': current_model_id,
        'device': str(device) if device else 'not initialized'
    })

@app.route('/generate', methods=['POST'])
def generate():
    """画像生成エンドポイント（改善版）"""
    try:
        data = request.json
        prompt = data.get('prompt', 'a pixel art character')
        negative_prompt = data.get('negative_prompt', '')
        steps = data.get('steps', 20)
        guidance_scale = data.get('guidance_scale', 7.5)
        width = data.get('width', 512)
        height = data.get('height', 512)
        pixel_size = data.get('pixel_size', 8)
        palette_size = data.get('palette_size', 16)
        model_id = data.get('model_id', 'runwayml/stable-diffusion-v1-5')
        
        # パイプライン初期化
        if not initialize_pipeline(model_id):
            return jsonify({'success': False, 'error': 'Failed to initialize model'}), 500
        
        # プロンプト強化
        enhanced_prompt = enhance_prompt_for_model(prompt, model_id)
        enhanced_negative = enhance_negative_prompt_for_model(negative_prompt, model_id)
        
        logger.info(f"Generating with prompt: {enhanced_prompt}")
        
        # 安全な画像生成
        with torch.inference_mode():
            image = safe_image_generation(
                pipeline,
                prompt=enhanced_prompt,
                negative_prompt=enhanced_negative,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=torch.Generator(device="cpu").manual_seed(42) if device.type == "mps" else None
            )
        
        # ピクセルアート処理
        pixel_art_image = apply_pixel_art_processing(image, pixel_size, palette_size)
        
        # Base64エンコード
        buffer = io.BytesIO()
        pixel_art_image.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # メモリクリーンアップ
        cleanup_memory()
        
        return jsonify({
            'success': True,
            'image': f"data:image/png;base64,{image_base64}",
            'enhanced_prompt': enhanced_prompt
        })
        
    except Exception as e:
        logger.error(f"Generation error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """利用可能なモデル一覧"""
    from model_configs import MODEL_CONFIGS
    return jsonify({
        'success': True,
        'models': list(MODEL_CONFIGS.keys()),
        'configs': MODEL_CONFIGS
    })

if __name__ == '__main__':
    logger.info("Starting Pixa - AI Pixel Art Generator Backend (Optimized)")
    
    if initialize_pipeline("runwayml/stable-diffusion-v1-5"):
        logger.info("Server starting on http://localhost:5001")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        logger.error("Failed to initialize. Server not started.")
