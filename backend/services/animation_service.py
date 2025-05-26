"""
Pixa - アニメーションサービス（リファクタリング後）
"""
from typing import List
from PIL import Image
import logging

from .animations import AnimationFactory

logger = logging.getLogger(__name__)


class AnimationService:
    """アニメーション生成サービス（リファクタリング後）"""
    
    @staticmethod
    def create_animation_frames(base_image: Image.Image,
                              animation_type: str,
                              frame_count: int = 8,
                              pixel_size: int = 8,
                              palette_size: int = 16) -> List[Image.Image]:
        """
        アニメーションフレームを生成
        
        Args:
            base_image: ベース画像
            animation_type: アニメーション種類
            frame_count: フレーム数
            pixel_size: ピクセルサイズ
            palette_size: パレットサイズ
            
        Returns:
            List[Image.Image]: 生成されたフレームリスト
        """
        return AnimationFactory.create_animation_frames(
            base_image=base_image,
            animation_type=animation_type,
            frame_count=frame_count,
            pixel_size=pixel_size,
            palette_size=palette_size
        )
    
    @staticmethod
    def get_supported_animation_types() -> List[str]:
        """サポートされているアニメーション種類を取得"""
        return AnimationFactory.get_all_animation_types()
    
    @staticmethod
    def get_animation_info(animation_type: str) -> dict:
        """アニメーション情報を取得"""
        return AnimationFactory.get_animation_info(animation_type)
    
    @staticmethod
    def get_game_animation_types() -> List[str]:
        """ゲーム開発向けアニメーション種類を取得"""
        return AnimationFactory.get_animation_types_by_category('game')
    
    @staticmethod
    def get_effect_animation_types() -> List[str]:
        """エフェクト系アニメーション種類を取得"""
        return AnimationFactory.get_animation_types_by_category('effect')


# グローバルサービスインスタンス
animation_service = AnimationService()
