"""
Pixa - 基本画像生成API
"""
from flask import Blueprint, request, jsonify
import logging

from services.ai_service import ai_service
from services.animation_service import animation_service
from utils.image_utils import apply_pixel_art_processing, image_to_base64
from config.settings import Config

logger = logging.getLogger(__name__)

# Blueprint作成
basic_routes = Blueprint('basic', __name__)


@basic_routes.route('/generate', methods=['POST'])
def generate_image():
    """基本的な画像生成エンドポイント"""
    try:
        data = request.json
        
        # パラメータ取得
        prompt = data.get('prompt', '')
        if not prompt.strip():
            return jsonify({'success': False, 'error': 'プロンプトが必要です'}), 400
        
        # モデルIDを取得して初期化
        model_id = data.get('model_id', Config.DEFAULT_MODEL_ID)
        if not ai_service.initialize_pipeline(model_id):
            return jsonify({'success': False, 'error': 'モデルの初期化に失敗しました'}), 500
        
        # パラメータの検証と取得
        negative_prompt = data.get('negative_prompt', '')
        width = data.get('width', Config.DEFAULT_IMAGE_SIZE)
        height = data.get('height', Config.DEFAULT_IMAGE_SIZE) 
        pixel_size = data.get('pixel_size', Config.DEFAULT_PIXEL_SIZE)
        palette_size = data.get('palette_size', Config.DEFAULT_PALETTE_SIZE)
        num_inference_steps = data.get('steps', 20)
        guidance_scale = data.get('guidance_scale', 7.5)
        seed = data.get('seed', None)
        
        # パラメータ検証
        img_params = Config.validate_image_params(width, height, pixel_size, palette_size)
        
        logger.info(f"Generating image: prompt='{prompt[:50]}...', size={img_params['width']}x{img_params['height']}")
        
        # AI画像生成
        generated_image = ai_service.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=img_params['width'],
            height=img_params['height'],
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        if generated_image is None:
            return jsonify({'success': False, 'error': '画像生成に失敗しました'}), 500
        
        # ピクセルアート処理
        pixel_art_image = apply_pixel_art_processing(
            generated_image, 
            img_params['pixel_size'], 
            img_params['palette_size']
        )
        
        # Base64エンコード
        image_base64 = image_to_base64(pixel_art_image)
        if image_base64 is None:
            return jsonify({'success': False, 'error': '画像エンコードに失敗しました'}), 500
        
        return jsonify({
            'success': True,
            'image': image_base64,
            'parameters': {
                'prompt': prompt,
                'model_id': model_id,
                'width': img_params['width'],
                'height': img_params['height'],
                'pixel_size': img_params['pixel_size'],
                'palette_size': img_params['palette_size']
            },
            'message': '画像生成が完了しました'
        })
        
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'画像生成中にエラーが発生しました: {str(e)}'
        }), 500


@basic_routes.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        device_info = ai_service.get_device_info()
        
        return jsonify({
            'status': 'healthy',
            'service': 'Pixa AI Pixel Art Generator',
            'device_info': device_info,
            'config': {
                'default_model': Config.DEFAULT_MODEL_ID,
                'max_image_size': Config.MAX_IMAGE_SIZE,
                'optimizations_enabled': Config.ENABLE_OPTIMIZATIONS
            }
        })
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@basic_routes.route('/models', methods=['GET'])
def get_available_models():
    """利用可能なモデル一覧"""
    try:
        # サポートされているモデル一覧
        models = [
            {
                'id': 'runwayml/stable-diffusion-v1-5',
                'name': 'Stable Diffusion v1.5',
                'type': 'base',
                'description': '汎用的な画像生成モデル'
            },
            {
                'id': 'stabilityai/stable-diffusion-xl-base-1.0',
                'name': 'Stable Diffusion XL',
                'type': 'xl',
                'description': '高解像度画像生成モデル'
            }
        ]
        
        return jsonify({
            'success': True,
            'models': models,
            'current_model': ai_service.get_current_model()
        })
        
    except Exception as e:
        logger.error(f"Models list error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
