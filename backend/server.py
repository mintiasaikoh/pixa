#!/usr/bin/env python3
"""
Pixa - AIピクセルアート生成アプリケーション
M2 Pro最適化 Flaskバックエンドサーバー
既存のStable Diffusion環境を活用したピクセルアート生成API
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import torch
from diffusers import StableDiffusionPipeline
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

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # フロントエンドとの通信を許可

# グローバル変数でパイプラインを保持
pipeline = None
device = None

def initialize_pipeline():
    """Stable Diffusion パイプラインを初期化"""
    global pipeline, device
    
    try:
        # M2 ProのMetal Performance Shaders (MPS) を優先使用
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("Using Metal Performance Shaders (MPS) for Apple Silicon")
        elif torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("Using CUDA GPU")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU")
        
        # Stable Diffusion v1.5 パイプライン読み込み
        model_id = "runwayml/stable-diffusion-v1-5"
        logger.info(f"Loading Stable Diffusion model: {model_id}")
        
        # MPSでの精度問題を避けるためfloat32を使用
        dtype = torch.float32 if device == torch.device("mps") else torch.float16
        if device == torch.device("cpu"):
            dtype = torch.float32
            
        pipeline = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            safety_checker=None,  # 高速化のためsafety checkerを無効化
            requires_safety_checker=False,
            use_safetensors=True
        )
        
        pipeline = pipeline.to(device)
        
        # メモリ効率の改善
        if device != torch.device("cpu"):
            pipeline.enable_attention_slicing()
            # xformersが利用可能な場合のみ有効化
            try:
                pipeline.enable_xformers_memory_efficient_attention()
            except Exception as e:
                logger.warning(f"xformers not available: {e}")
                logger.info("Continuing without xformers optimization")
        
        logger.info("Pipeline initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        return False

def apply_pixel_art_processing(image, pixel_size=8, palette_size=16):
    """
    生成された画像にピクセルアート風の後処理を適用
    
    Args:
        image: PIL Image
        pixel_size: ピクセルサイズ（数値が大きいほど粗い）
        palette_size: カラーパレットサイズ
    
    Returns:
        PIL Image: ピクセルアート風に処理された画像
    """
    # 1. 画像を縮小してピクセル感を作る
    original_size = image.size
    small_size = (original_size[0] // pixel_size, original_size[1] // pixel_size)
    
    # 最小サイズを保証
    small_size = (max(small_size[0], 16), max(small_size[1], 16))
    
    # 縮小（アンチエイリアシング無し）
    image_small = image.resize(small_size, Image.NEAREST)
    
    # 2. カラーパレットを制限
    if palette_size < 256:
        # カラー量子化
        image_small = image_small.quantize(colors=palette_size, method=Image.MEDIANCUT)
        image_small = image_small.convert('RGB')
    
    # 3. 元のサイズに拡大（ピクセル感を保持）
    pixel_art = image_small.resize(original_size, Image.NEAREST)
    
    return pixel_art

def translate_japanese_to_english(text):
    """
    日本語プロンプトを英語に翻訳（基本的な単語辞書ベース）
    """
    # 日本語→英語翻訳辞書
    translation_dict = {
        # 動物
        '猫': 'cat',
        '犬': 'dog',
        '鳥': 'bird',
        '魚': 'fish',
        'ドラゴン': 'dragon',
        '竜': 'dragon',
        '馬': 'horse',
        'うさぎ': 'rabbit',
        'ウサギ': 'rabbit',
        
        # キャラクター
        '騎士': 'knight',
        '魔法使い': 'wizard',
        '勇者': 'hero',
        '王様': 'king',
        '女王': 'queen',
        '忍者': 'ninja',
        '侍': 'samurai',
        '戦士': 'warrior',
        
        # 場所・建物
        '城': 'castle',
        '森': 'forest',
        '山': 'mountain',
        '海': 'ocean',
        '空': 'sky',
        '街': 'town',
        '村': 'village',
        '家': 'house',
        '塔': 'tower',
        
        # 乗り物
        '船': 'ship',
        '宇宙船': 'spaceship',
        '車': 'car',
        '飛行機': 'airplane',
        
        # 形容詞
        '可愛い': 'cute',
        'かわいい': 'cute',
        '美しい': 'beautiful',
        '大きい': 'big',
        '小さい': 'small',
        '強い': 'strong',
        '魔法の': 'magical',
        '神秘的な': 'mysterious',
        '古い': 'old',
        '新しい': 'new',
        '赤い': 'red',
        '青い': 'blue',
        '緑の': 'green',
        '黄色い': 'yellow',
        '黒い': 'black',
        '白い': 'white',
        
        # 動作
        '飛んでいる': 'flying',
        '寝ている': 'sleeping',
        '走っている': 'running',
        '戦っている': 'fighting',
        '笑っている': 'smiling',
        '歩く': 'walk',
        '走る': 'run',
        'ジャンプ': 'jump',
        '待機': 'idle',
        'アイドル': 'idle',
        '点滅': 'blink',
        '揺れる': 'sway',
        '回転': 'rotate',
        'バウンス': 'bounce',
        '光る': 'glow',
        
        # その他
        '剣': 'sword',
        '盾': 'shield',
        '魔法': 'magic',
        '宝物': 'treasure',
        '星': 'star',
        '月': 'moon',
        '太陽': 'sun',
        '花': 'flower',
        '木': 'tree',
        '水': 'water',
        '火': 'fire',
        '雷': 'lightning',
        '雪': 'snow',
        '雲': 'cloud',
        
        # ネガティブプロンプト用
        'ぼやけた': 'blurry',
        'ぼけた': 'blurry',
        '低品質': 'low quality',
        '低画質': 'low quality',
        '悪い': 'bad',
        '変な': 'weird',
        'おかしい': 'weird',
        '歪んだ': 'distorted',
        '崩れた': 'broken',
        '汚い': 'dirty',
        'きたない': 'dirty',
        '醜い': 'ugly',
        'みにくい': 'ugly',
        '不自然な': 'unnatural',
        '暗い': 'dark',
        '薄い': 'faded',
        'ノイズ': 'noise',
        '粗い': 'rough',
        'あらい': 'rough',
        '解剖学的に': 'anatomy',
        '指が': 'fingers',
        '手が': 'hands',
        '余分な': 'extra',
        '欠けた': 'missing',
        '重複した': 'duplicate'
    }
    
    # 日本語が含まれているかチェック
    if not re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text):
        return text  # 日本語が含まれていない場合はそのまま返す
    
    logger.info(f"Japanese prompt detected: {text}")
    
    # 単語ベースで翻訳
    translated = text
    for jp_word, en_word in translation_dict.items():
        translated = translated.replace(jp_word, en_word)
    
    # 基本的な助詞や接続詞を処理
    translated = re.sub(r'[のがをにはでと、。]', ' ', translated)
    translated = re.sub(r'\s+', ' ', translated).strip()
    
    logger.info(f"Translated to: {translated}")
    return translated

def enhance_pixel_art_prompt(prompt):
    """
    プロンプトにピクセルアート特化のキーワードを追加
    """
    # まず日本語を英語に翻訳
    prompt = translate_japanese_to_english(prompt)
    
    pixel_keywords = [
        "pixel art",
        "8-bit style",
        "retro game",
        "sprite",
        "low resolution",
        "pixelated",
        "video game art"
    ]
    
    # 既にピクセルアート関連キーワードが含まれていない場合追加
    prompt_lower = prompt.lower()
    if not any(keyword in prompt_lower for keyword in pixel_keywords):
        prompt = f"{prompt}, pixel art style, 8-bit, retro game sprite"
    
    return prompt

def create_animation_frames(base_image, animation_type, frame_count, pixel_size, palette_size):
    """
    ベース画像からアニメーションフレームを生成
    
    Args:
        base_image: PIL Image - ベースとなる画像
        animation_type: str - アニメーションタイプ
        frame_count: int - フレーム数
        pixel_size: int - ピクセルサイズ
        palette_size: int - パレットサイズ
    
    Returns:
        list of PIL Images - アニメーションフレーム
    """
    frames = []
    
    if animation_type == "idle":
        # アイドルアニメーション（上下に微妙に動く）
        for i in range(frame_count):
            frame = base_image.copy()
            # サインカーブで滑らかな上下動
            offset_y = int(5 * math.sin(2 * math.pi * i / frame_count))
            
            # 画像をシフト
            new_frame = Image.new('RGB', base_image.size, (0, 0, 0))
            new_frame.paste(frame, (0, offset_y))
            
            # ピクセルアート処理
            frame = apply_pixel_art_processing(new_frame, pixel_size, palette_size)
            frames.append(frame)
            
    elif animation_type == "walk":
        # 歩行アニメーション（左右に傾く）
        for i in range(frame_count):
            frame = base_image.copy()
            # 回転角度
            angle = 5 * math.sin(2 * math.pi * i / frame_count)
            
            # 回転
            frame = frame.rotate(angle, expand=False, fillcolor=(0, 0, 0))
            
            # ピクセルアート処理
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
            
    elif animation_type == "glow":
        # 発光エフェクト（明るさを変化）
        for i in range(frame_count):
            frame = base_image.copy()
            # 明るさの変化
            brightness_factor = 0.8 + 0.4 * math.sin(2 * math.pi * i / frame_count)
            
            # 明度調整
            enhancer = ImageEnhance.Brightness(frame)
            frame = enhancer.enhance(brightness_factor)
            
            # ピクセルアート処理
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
            
    elif animation_type == "bounce":
        # バウンスアニメーション
        for i in range(frame_count):
            frame = base_image.copy()
            # バウンス計算
            t = i / (frame_count - 1) if frame_count > 1 else 0
            height = abs(math.sin(math.pi * t)) * 20
            
            # 画像をシフト
            new_frame = Image.new('RGB', base_image.size, (0, 0, 0))
            new_frame.paste(frame, (0, -int(height)))
            
            # ピクセルアート処理
            frame = apply_pixel_art_processing(new_frame, pixel_size, palette_size)
            frames.append(frame)
            
    else:  # default or "rotate"
        # 回転アニメーション
        for i in range(frame_count):
            frame = base_image.copy()
            angle = 360 * i / frame_count
            
            # 回転
            frame = frame.rotate(angle, expand=False, fillcolor=(0, 0, 0))
            
            # ピクセルアート処理
            frame = apply_pixel_art_processing(frame, pixel_size, palette_size)
            frames.append(frame)
    
    return frames

@app.route('/')
def index():
    """メインページを提供"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'healthy',
        'pipeline_loaded': pipeline is not None,
        'device': str(device) if device else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/generate', methods=['POST'])
def generate_pixel_art():
    """
    ピクセルアート生成エンドポイント
    """
    if pipeline is None:
        return jsonify({'error': 'Pipeline not initialized'}), 500
    
    try:
        data = request.get_json()
        
        # パラメータ取得
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', 'blurry, low quality, bad anatomy')
        num_inference_steps = data.get('steps', 20)
        guidance_scale = data.get('guidance_scale', 7.5)
        seed = data.get('seed', None)
        width = data.get('width', 512)
        height = data.get('height', 512)
        pixel_size = data.get('pixel_size', 8)
        palette_size = data.get('palette_size', 16)
        
        # プロンプト強化
        enhanced_prompt = enhance_pixel_art_prompt(prompt)
        # ネガティブプロンプトも日本語対応
        enhanced_negative_prompt = translate_japanese_to_english(negative_prompt)
        
        # シード設定（MPSではCPUジェネレーターを使用）
        if seed is not None:
            if device == torch.device("mps"):
                generator = torch.Generator().manual_seed(seed)  # CPUジェネレーター
            else:
                generator = torch.Generator(device=device).manual_seed(seed)
        else:
            generator = None
        
        logger.info(f"Generating image with prompt: {enhanced_prompt}")
        logger.info(f"Parameters: steps={num_inference_steps}, guidance={guidance_scale}, size={width}x{height}")
        
        # 画像生成
        try:
            with torch.no_grad():
                result = pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=enhanced_negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height,
                    generator=generator
                )
            
            logger.info("Image generation completed successfully")
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
        
        # 生成された画像を取得
        image = result.images[0]
        logger.info(f"Generated image size: {image.size}, mode: {image.mode}")
        
        # 画像が空でないかチェック
        image_array = np.array(image)
        logger.info(f"Image array shape: {image_array.shape}, min: {image_array.min()}, max: {image_array.max()}")
        
        # 真っ黒な画像の場合はエラーを報告
        if image_array.max() == 0:
            logger.warning("Generated image is completely black!")
            # デバッグ用に基本的な画像生成を試す
            logger.info("Attempting basic generation without pixel art processing...")
        
        # ピクセルアート風後処理
        pixel_art_image = apply_pixel_art_processing(
            image, 
            pixel_size=pixel_size, 
            palette_size=palette_size
        )
        
        logger.info(f"Pixel art processed image size: {pixel_art_image.size}")
        
        # 画像をBase64エンコード
        buffer = io.BytesIO()
        pixel_art_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f"data:image/png;base64,{image_base64}",
            'parameters': {
                'prompt': enhanced_prompt,
                'negative_prompt': enhanced_negative_prompt,
                'steps': num_inference_steps,
                'guidance_scale': guidance_scale,
                'seed': seed,
                'width': width,
                'height': height,
                'pixel_size': pixel_size,
                'palette_size': palette_size
            }
        })
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/presets', methods=['GET'])
def get_presets():
    """プリセット一覧を返す"""
    presets = {
        '8bit': {
            'name': '8-bit',
            'description': 'ファミコン風のドット絵',
            'pixel_size': 8,
            'palette_size': 8,
            'steps': 20,
            'guidance_scale': 7.5
        },
        '16bit': {
            'name': '16-bit',
            'description': 'スーパーファミコン風の細かいドット',
            'pixel_size': 6,
            'palette_size': 16,
            'steps': 25,
            'guidance_scale': 8.0
        },
        'gameboy': {
            'name': 'ゲームボーイ風',
            'description': '緑っぽいモノトーン4色',
            'pixel_size': 10,
            'palette_size': 4,
            'steps': 20,
            'guidance_scale': 7.0
        },
        'minimal': {
            'name': 'ミニマル',
            'description': 'シンプルで洗練されたデザイン',
            'pixel_size': 12,
            'palette_size': 6,
            'steps': 15,
            'guidance_scale': 6.5
        },
        'detailed': {
            'name': '高精細',
            'description': '細かく美しい表現',
            'pixel_size': 4,
            'palette_size': 32,
            'steps': 30,
            'guidance_scale': 8.5
        }
    }
    
    return jsonify(presets)

@app.route('/generate_animation', methods=['POST'])
def generate_animation():
    """
    動くGIFを生成するエンドポイント
    """
    if pipeline is None:
        return jsonify({'error': 'Pipeline not initialized'}), 500
    
    try:
        data = request.json
        
        # パラメータ取得
        prompt = data.get('prompt', 'pixel art character')
        animation_type = data.get('animation_type', 'idle')
        frame_count = min(max(data.get('frame_count', 4), 2), 16)  # 2-16フレーム
        fps = min(max(data.get('fps', 10), 5), 30)  # 5-30 FPS
        width = min(max(data.get('width', 512), 256), 1024)
        height = min(max(data.get('height', 512), 256), 1024)
        pixel_size = min(max(data.get('pixel_size', 8), 2), 20)
        palette_size = min(max(data.get('palette_size', 16), 4), 64)
        num_inference_steps = min(max(data.get('steps', 20), 1), 50)
        guidance_scale = data.get('guidance_scale', 7.5)
        negative_prompt = data.get('negative_prompt', '')
        seed = data.get('seed', None)
        
        # プロンプト拡張
        enhanced_prompt = enhance_pixel_art_prompt(prompt)
        # ネガティブプロンプトも日本語対応
        enhanced_negative_prompt = translate_japanese_to_english(negative_prompt)
        if animation_type in ['walk', 'run']:
            enhanced_prompt += ", character sprite sheet, walking animation"
        elif animation_type == 'idle':
            enhanced_prompt += ", character standing, idle pose"
        
        # シード設定
        if seed is not None:
            if device == torch.device("mps"):
                generator = torch.Generator().manual_seed(seed)
            else:
                generator = torch.Generator(device=device).manual_seed(seed)
        else:
            generator = None
        
        logger.info(f"Generating animation with prompt: {enhanced_prompt}")
        logger.info(f"Animation parameters: type={animation_type}, frames={frame_count}, fps={fps}")
        
        # ベース画像生成
        with torch.no_grad():
            result = pipeline(
                prompt=enhanced_prompt,
                negative_prompt=enhanced_negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=generator
            )
        
        base_image = result.images[0]
        logger.info("Base image generated successfully")
        
        # アニメーションフレーム生成
        frames = create_animation_frames(
            base_image,
            animation_type,
            frame_count,
            pixel_size,
            palette_size
        )
        
        # GIFに変換
        gif_buffer = io.BytesIO()
        
        # imageioを使用してGIFを作成
        duration = 1000 / fps  # ミリ秒単位
        imageio.mimsave(
            gif_buffer,
            frames,
            format='GIF',
            duration=duration,
            loop=0  # 無限ループ
        )
        
        gif_buffer.seek(0)
        
        # Base64エンコード
        gif_base64 = base64.b64encode(gif_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/gif;base64,{gif_base64}',
            'animation_type': animation_type,
            'frame_count': frame_count,
            'fps': fps,
            'message': 'Animation generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Animation generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/animate_existing', methods=['POST'])
def animate_existing_image():
    """
    既存の画像をアニメーション化するエンドポイント
    """
    try:
        data = request.json
        
        # パラメータ取得
        base_image_data = data.get('base_image', '')
        animation_type = data.get('animation_type', 'idle')
        frame_count = min(max(data.get('frame_count', 4), 2), 16)
        fps = min(max(data.get('fps', 10), 5), 30)
        pixel_size = min(max(data.get('pixel_size', 8), 2), 20)
        palette_size = min(max(data.get('palette_size', 16), 4), 64)
        
        if not base_image_data:
            return jsonify({
                'success': False,
                'error': 'No base image provided'
            }), 400
        
        # Base64データから画像を復元
        try:
            # データURIスキームを削除
            if base_image_data.startswith('data:image'):
                base_image_data = base_image_data.split(',')[1]
            
            # Base64デコード
            image_bytes = base64.b64decode(base_image_data)
            base_image = Image.open(io.BytesIO(image_bytes))
            
            # RGBに変換（透明度がある場合）
            if base_image.mode != 'RGB':
                base_image = base_image.convert('RGB')
                
        except Exception as e:
            logger.error(f"Failed to decode base image: {e}")
            return jsonify({
                'success': False,
                'error': 'Invalid base image data'
            }), 400
        
        logger.info(f"Animating existing image: type={animation_type}, frames={frame_count}, fps={fps}")
        
        # アニメーションフレーム生成
        frames = create_animation_frames(
            base_image,
            animation_type,
            frame_count,
            pixel_size,
            palette_size
        )
        
        # GIFに変換
        gif_buffer = io.BytesIO()
        duration = 1000 / fps  # ミリ秒単位
        imageio.mimsave(
            gif_buffer,
            frames,
            format='GIF',
            duration=duration,
            loop=0  # 無限ループ
        )
        
        gif_buffer.seek(0)
        
        # Base64エンコード
        gif_base64 = base64.b64encode(gif_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/gif;base64,{gif_base64}',
            'animation_type': animation_type,
            'frame_count': frame_count,
            'fps': fps,
            'message': 'Animation created from existing image'
        })
        
    except Exception as e:
        logger.error(f"Animation from existing image error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Pixa - AI Pixel Art Generator Backend")
    
    # パイプライン初期化
    if initialize_pipeline():
        logger.info("Server starting on http://localhost:5001")
        logger.info("Open your browser to http://localhost:5001 to use the application")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        logger.error("Failed to initialize. Server not started.")