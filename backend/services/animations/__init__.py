"""
Pixa - アニメーション統合インターフェース
"""
from .game_animations import GameAnimations, GAME_ANIMATION_TYPES
from .effect_animations import EffectAnimations, EFFECT_ANIMATION_TYPES
from .animation_base import AnimationBase

from typing import List
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# 全アニメーション種類の統合
ALL_ANIMATION_TYPES = GAME_ANIMATION_TYPES + EFFECT_ANIMATION_TYPES


class AnimationFactory:
    """アニメーション生成のファクトリークラス"""
    
    @staticmethod
    def create_animation_frames(base_image: Image.Image,
                              animation_type: str,
                              frame_count: int = 8,
                              pixel_size: int = 8,
                              palette_size: int = 16,
                              **kwargs) -> List[Image.Image]:
        """
        アニメーション種類に応じて適切なクラスでフレームを生成
        
        Args:
            base_image: ベース画像
            animation_type: アニメーション種類
            frame_count: フレーム数
            pixel_size: ピクセルサイズ
            palette_size: パレットサイズ
            **kwargs: その他のパラメータ
            
        Returns:
            List[Image.Image]: 生成されたフレームリスト
        """
        try:
            # アニメーション種類に応じて適切なクラスを選択
            if animation_type in GAME_ANIMATION_TYPES:
                return GameAnimations.create_frames(
                    base_image, animation_type, frame_count, 
                    pixel_size, palette_size, **kwargs
                )
            elif animation_type in EFFECT_ANIMATION_TYPES:
                return EffectAnimations.create_frames(
                    base_image, animation_type, frame_count, 
                    pixel_size, palette_size, **kwargs
                )
            else:
                logger.warning(f"Unknown animation type: {animation_type}, using default")
                return GameAnimations.create_frames(
                    base_image, 'idle_breathing', frame_count, 
                    pixel_size, palette_size, **kwargs
                )
                
        except Exception as e:
            logger.error(f"Animation creation failed: {str(e)}")
            return [base_image]  # エラー時は元画像を返す
    
    @staticmethod
    def get_animation_info(animation_type: str) -> dict:
        """アニメーション情報を取得"""
        animation_info = {
            # ゲーム開発向け
            'walk_cycle': {'name': '歩行サイクル', 'category': 'game', 'description': '左右の足を交互に動かす歩行アニメーション'},
            'idle_breathing': {'name': 'アイドル（呼吸）', 'category': 'game', 'description': '待機時の微細な呼吸による上下動'},
            'attack_slash': {'name': '攻撃（斬撃）', 'category': 'game', 'description': '予備動作→攻撃→戻りの一連の動作'},
            'jump_landing': {'name': 'ジャンプ・着地', 'category': 'game', 'description': 'しゃがみ→ジャンプ→着地のモーション'},
            'walk_4direction': {'name': '4方向歩行', 'category': 'game', 'description': '上下左右4方向の歩行サイクル'},
            'damage_flash': {'name': 'ダメージフラッシュ', 'category': 'game', 'description': '被ダメージ時の点滅と後退'},
            
            # エフェクト系
            'glitch_wave': {'name': 'グリッチウェーブ', 'category': 'effect', 'description': 'デジタル風の波打ちエフェクト'},
            'heartbeat': {'name': 'ハートビート', 'category': 'effect', 'description': '脈動するような拡大縮小'},
            'spiral': {'name': 'スパイラル', 'category': 'effect', 'description': '螺旋状に回転しながら拡大縮小'},
            'pixel_rain': {'name': 'ピクセルレイン', 'category': 'effect', 'description': 'ピクセルが雨のように落ちて再構築'},
            'wave_distortion': {'name': '波状歪み', 'category': 'effect', 'description': '水面のような波打ち効果'},
            'explode_reassemble': {'name': '爆発・再集合', 'category': 'effect', 'description': 'パーツが飛び散って戻ってくる'},
            'split_merge': {'name': '分裂・結合', 'category': 'effect', 'description': '画像が分裂して回転しながら戻る'},
            'electric_shock': {'name': '電撃エフェクト', 'category': 'effect', 'description': '稲妻のような歪み'},
            'rubberband': {'name': 'ラバーバンド', 'category': 'effect', 'description': 'ゴムのように伸び縮み'},
        }
        
        return animation_info.get(animation_type, {
            'name': animation_type,
            'category': 'unknown',
            'description': 'Unknown animation type'
        })
    
    @staticmethod
    def get_all_animation_types() -> List[str]:
        """全アニメーション種類を取得"""
        return ALL_ANIMATION_TYPES.copy()
    
    @staticmethod
    def get_animation_types_by_category(category: str) -> List[str]:
        """カテゴリ別のアニメーション種類を取得"""
        if category == 'game':
            return GAME_ANIMATION_TYPES.copy()
        elif category == 'effect':
            return EFFECT_ANIMATION_TYPES.copy()
        else:
            return []


# 後方互換性のためのエイリアス
def create_animation_frames(*args, **kwargs):
    """後方互換性のためのラッパー関数"""
    return AnimationFactory.create_animation_frames(*args, **kwargs)


# サービスインスタンス（後方互換性のため）
class AnimationService:
    """後方互換性のためのラッパークラス"""
    
    @staticmethod
    def create_animation_frames(*args, **kwargs):
        return AnimationFactory.create_animation_frames(*args, **kwargs)


animation_service = AnimationService()
