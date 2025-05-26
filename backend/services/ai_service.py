"""
Pixa - AI画像生成サービス
"""
import torch
import logging
from typing import Optional, Dict, Any, List
from PIL import Image
from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline, DiffusionPipeline
import gc

from config.settings import Config

logger = logging.getLogger(__name__)


class AIService:
    """AI画像生成サービスクラス"""
    
    def __init__(self):
        self.pipeline = None
        self.device = None
        self.current_model_id = None
        self.dtype = None
        
        # 最適化設定を適用
        Config.setup_optimizations()
    
    def initialize_pipeline(self, model_id: str = None) -> bool:
        """パイプラインを初期化"""
        model_id = model_id or Config.DEFAULT_MODEL_ID
        
        try:
            # デバイス設定
            self.device = Config.get_device()
            self.dtype = Config.get_dtype(self.device)
            
            logger.info(f"Using device: {self.device}, dtype: {self.dtype}")
            
            # モデルが変更された場合のみ読み込み
            if self.current_model_id != model_id or self.pipeline is None:
                self._load_pipeline(model_id)
                self.current_model_id = model_id
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {str(e)}")
            return False
    
    def _load_pipeline(self, model_id: str):
        """パイプラインを読み込み"""
        # 既存パイプラインのクリア
        if self.pipeline is not None:
            del self.pipeline
            self._clear_memory()
        
        logger.info(f"Loading model: {model_id}")
        
        # SDXL判定
        is_sdxl = "xl" in model_id.lower()
        
        # パイプライン読み込み
        if is_sdxl:
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=self.dtype,
                use_safetensors=True,
                variant="fp16" if self.dtype == torch.float16 else None
            )
        else:
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=self.dtype,
                use_safetensors=True,
                variant="fp16" if self.dtype == torch.float16 else None
            )
        
        # パイプライン設定
        self.pipeline = self.pipeline.to(self.device)
        
        if self.device != torch.device("mps"):
            self.pipeline.enable_memory_efficient_attention()
        
        logger.info(f"Model loaded successfully: {model_id}")
    
    def _clear_memory(self):
        """メモリクリア"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif self.device == torch.device("mps"):
            torch.mps.empty_cache()
        gc.collect()
    
    def generate_image(self, 
                      prompt: str,
                      negative_prompt: str = "",
                      width: int = 512,
                      height: int = 512,
                      num_inference_steps: int = 20,
                      guidance_scale: float = 7.5,
                      seed: Optional[int] = None) -> Optional[Image.Image]:
        """画像生成"""
        if not self.pipeline:
            logger.error("Pipeline not initialized")
            return None
        
        try:
            # パラメータ検証
            params = Config.validate_image_params(width, height, 0, 0)
            width, height = params['width'], params['height']
            
            # ジェネレーター設定
            generator = None
            if seed is not None:
                if self.device == torch.device("mps"):
                    generator = torch.Generator().manual_seed(seed)
                else:
                    generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # 画像生成
            with torch.no_grad():
                result = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                )
                
                return result.images[0]
        
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return None
    
    def is_initialized(self) -> bool:
        """初期化済みかチェック"""
        return self.pipeline is not None
    
    def get_current_model(self) -> Optional[str]:
        """現在のモデルIDを取得"""
        return self.current_model_id
    
    def get_device_info(self) -> Dict[str, Any]:
        """デバイス情報を取得"""
        return {
            'device': str(self.device) if self.device else None,
            'dtype': str(self.dtype) if self.dtype else None,
            'model_id': self.current_model_id,
            'initialized': self.is_initialized()
        }


# グローバルサービスインスタンス
ai_service = AIService()
