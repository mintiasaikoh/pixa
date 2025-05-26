"""
Pixa - アニメーション関連API
"""
from flask import Blueprint, request, jsonify
import logging
import os
import tempfile
from datetime import datetime

from services.ai_service import ai_service
from services.animation_service import animation_service
from services.gif_optimization_service import gif_optimization_service
from utils.image_utils import base64_to_image, image_to_base64
from config.settings import Config, ANIMATION_TYPES

logger = logging.getLogger(__name__)

# Blueprint作成
animation_routes = Blueprint('animation', __name__)


@animation_routes.route('/generate_optimized_animation', methods=['POST'])
def generate_optimized_animation():
    """差分合成最適化GIFを生成するエンドポイント"""
    try:
        data = request.json
        
        # 既存画像を使用する場合
        existing_image_data = data.get('existing_image')
        if not existing_image_data:
            return jsonify({
                'success': False,
                'error': '既存画像データが必要です'
            }), 400
        
        # Base64から画像を復元
        base_image = base64_to_image(existing_image_data)
        if base_image is None:
            return jsonify({
                'success': False,
                'error': '画像データの解析に失敗しました'
            }), 400
        
        # パラメータ取得と検証
        animation_type = data.get('animation_type', 'heartbeat')
        if animation_type not in ANIMATION_TYPES:
            animation_type = 'heartbeat'
        
        frame_count = data.get('frame_count', 8)
        pixel_size = data.get('pixel_size', Config.DEFAULT_PIXEL_SIZE)
        palette_size = data.get('palette_size', Config.DEFAULT_PALETTE_SIZE)
        tolerance = data.get('tolerance', Config.DEFAULT_TOLERANCE)
        duration_ms = data.get('duration', Config.DEFAULT_DURATION)
        
        # パラメータ検証
        anim_params = Config.validate_animation_params(frame_count, 10)  # FPSは使用しない
        opt_params = Config.validate_optimization_params(tolerance, duration_ms)
        img_params = Config.validate_image_params(0, 0, pixel_size, palette_size)
        
        logger.info(f"Generating optimized animation: {animation_type}, frames={anim_params['frame_count']}")
        
        # アニメーションフレーム生成
        frames = animation_service.create_animation_frames(
            base_image=base_image,
            animation_type=animation_type,
            frame_count=anim_params['frame_count'],
            pixel_size=img_params['pixel_size'],
            palette_size=img_params['palette_size']
        )
        
        if not frames:
            return jsonify({
                'success': False,
                'error': 'アニメーションフレームの生成に失敗しました'
            }), 500
        
        # 一時ファイルで差分合成最適化GIF生成
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 差分合成最適化GIF保存
            success, file_size = gif_optimization_service.save_optimized_gif(
                frames=frames,
                output_path=temp_path,
                duration=opt_params['duration'],
                loop=0,
                tolerance=opt_params['tolerance']
            )
            
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'GIFファイルの生成に失敗しました'
                }), 500
            
            # GIFファイルを読み込んでBase64エンコード
            with open(temp_path, 'rb') as f:
                gif_data = f.read()
            
            gif_base64 = f"data:image/gif;base64,{gif_data.hex()}"
            
            # 統計情報取得
            stats = gif_optimization_service.get_optimization_stats(frames, opt_params['tolerance'])
            
            return jsonify({
                'success': True,
                'image': gif_base64,
                'animation_type': animation_type,
                'frame_count': len(frames),
                'file_size': file_size,
                'file_size_kb': round(file_size / 1024, 1),
                'tolerance': opt_params['tolerance'],
                'duration_ms': opt_params['duration'],
                'optimization_stats': stats,
                'optimized': True,
                'message': f'差分合成最適化GIF生成完了 ({file_size:,} bytes)'
            })
            
        finally:
            # 一時ファイル削除
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Optimized animation generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'最適化GIF生成中にエラーが発生しました: {str(e)}'
        }), 500


@animation_routes.route('/batch_generate_optimized_animations', methods=['POST'])
def batch_generate_optimized_animations():
    """全種類の差分合成最適化GIFを一括生成"""
    try:
        data = request.json
        existing_image_data = data.get('existing_image')
        
        if not existing_image_data:
            return jsonify({
                'success': False,
                'error': '既存画像データが必要です'
            }), 400
        
        # Base64から画像を復元
        base_image = base64_to_image(existing_image_data)
        if base_image is None:
            return jsonify({
                'success': False,
                'error': '画像データの解析に失敗しました'
            }), 400
        
        # パラメータ取得
        pixel_size = data.get('pixel_size', Config.DEFAULT_PIXEL_SIZE)
        palette_size = data.get('palette_size', Config.DEFAULT_PALETTE_SIZE)
        
        img_params = Config.validate_image_params(0, 0, pixel_size, palette_size)
        
        logger.info(f"Batch generating optimized animations")
        
        # 結果を格納
        batch_results = {}
        total_size = 0
        success_count = 0
        
        for anim_type in ANIMATION_TYPES:
            try:
                # アニメーションフレーム生成
                frames = animation_service.create_animation_frames(
                    base_image=base_image,
                    animation_type=anim_type,
                    frame_count=16,  # 一括生成では固定
                    pixel_size=img_params['pixel_size'],
                    palette_size=img_params['palette_size']
                )
                
                if frames:
                    # 一時ファイルで差分合成最適化GIF生成
                    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    try:
                        success, file_size = gif_optimization_service.save_optimized_gif(
                            frames=frames,
                            output_path=temp_path,
                            duration=100,
                            loop=0,
                            tolerance=3
                        )
                        
                        if success:
                            with open(temp_path, 'rb') as f:
                                gif_data = f.read()
                            
                            gif_base64 = base64.b64encode(gif_data).decode('utf-8')
                            gif_base64 = f"data:image/gif;base64,{gif_base64}"
                            
                            batch_results[anim_type] = {
                                'success': True,
                                'image': gif_base64,
                                'file_size': file_size,
                                'file_size_kb': round(file_size / 1024, 1)
                            }
                            
                            total_size += file_size
                            success_count += 1
                        else:
                            batch_results[anim_type] = {
                                'success': False,
                                'error': 'GIF生成に失敗しました'
                            }
                    
                    finally:
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                else:
                    batch_results[anim_type] = {
                        'success': False,
                        'error': 'フレーム生成に失敗しました'
                    }
                    
            except Exception as e:
                batch_results[anim_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        return jsonify({
            'success': True,
            'animations': batch_results,
            'statistics': {
                'success_count': success_count,
                'total_count': len(ANIMATION_TYPES),
                'total_size': total_size,
                'total_size_kb': round(total_size / 1024, 1),
                'average_size_kb': round(total_size / 1024 / success_count, 1) if success_count > 0 else 0
            },
            'message': f'{success_count}/{len(ANIMATION_TYPES)} アニメーション生成完了'
        })
        
    except Exception as e:
        logger.error(f"Batch optimized animation generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'一括最適化GIF生成中にエラーが発生しました: {str(e)}'
        }), 500


@animation_routes.route('/animation_types', methods=['GET'])
def get_animation_types():
    """利用可能なアニメーションタイプ一覧"""
    try:
        animation_info = [
            # 🎮 実用的なゲーム開発向けアニメーション
            {'id': 'walk_cycle', 'name': '歩行サイクル', 'description': '左右の足を交互に動かす歩行アニメーション', 'category': 'game'},
            {'id': 'idle_breathing', 'name': 'アイドル（呼吸）', 'description': '待機時の微細な呼吸による上下動', 'category': 'game'},
            {'id': 'attack_slash', 'name': '攻撃（斬撃）', 'description': '予備動作→攻撃→戻りの一連の動作', 'category': 'game'},
            {'id': 'jump_landing', 'name': 'ジャンプ・着地', 'description': 'しゃがみ→ジャンプ→着地のモーション', 'category': 'game'},
            {'id': 'walk_4direction', 'name': '4方向歩行', 'description': '上下左右4方向の歩行サイクル', 'category': 'game'},
            {'id': 'damage_flash', 'name': 'ダメージフラッシュ', 'description': '被ダメージ時の点滅と後退', 'category': 'game'},
            
            # 🎨 エフェクト系アニメーション
            {'id': 'glitch_wave', 'name': 'グリッチウェーブ', 'description': 'デジタル風の波打ちエフェクト', 'category': 'effect'},
            {'id': 'explode_reassemble', 'name': '爆発・再集合', 'description': 'パーツが飛び散って戻ってくる', 'category': 'effect'},
            {'id': 'pixel_rain', 'name': 'ピクセルレイン', 'description': 'ピクセルが雨のように落ちて再構築', 'category': 'effect'},
            {'id': 'wave_distortion', 'name': '波状歪み', 'description': '水面のような波打ち効果', 'category': 'effect'},
            {'id': 'heartbeat', 'name': 'ハートビート', 'description': '脈動するような拡大縮小', 'category': 'effect'},
            {'id': 'spiral', 'name': 'スパイラル', 'description': '螺旋状に回転しながら拡大縮小', 'category': 'effect'},
            {'id': 'split_merge', 'name': '分裂・結合', 'description': '画像が分裂して回転しながら戻る', 'category': 'effect'},
            {'id': 'electric_shock', 'name': '電撃エフェクト', 'description': '稲妻のような歪み', 'category': 'effect'},
            {'id': 'rubberband', 'name': 'ラバーバンド', 'description': 'ゴムのように伸び縮み', 'category': 'effect'},
        ]
        
        return jsonify({
            'success': True,
            'animation_types': animation_info,
            'total_count': len(animation_info)
        })
        
    except Exception as e:
        logger.error(f"Animation types error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
