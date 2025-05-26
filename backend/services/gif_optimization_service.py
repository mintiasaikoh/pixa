"""
Pixa - GIF最適化サービス
差分合成最適化によるファイルサイズ削減
"""
import os
import numpy as np
from PIL import Image
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GifOptimizationService:
    """GIF最適化サービス"""
    
    @staticmethod
    def create_frame_difference(previous_frame: Optional[Image.Image],
                              current_frame: Image.Image,
                              tolerance: int = 3) -> Image.Image:
        """フレーム間の差分を検出し、変更のない部分を最適化"""
        
        if previous_frame is None:
            # 最初のフレームはそのまま返す（RGBのまま）
            return current_frame.convert('RGB')
        
        # RGBに変換して比較
        prev_rgb = previous_frame.convert('RGB')
        curr_rgb = current_frame.convert('RGB')
        
        # numpy配列に変換
        prev_array = np.array(prev_rgb)
        curr_array = np.array(curr_rgb)
        
        # ピクセル単位での差分を計算
        diff = np.abs(prev_array.astype(int) - curr_array.astype(int))
        pixel_diff = np.max(diff, axis=2)  # RGB最大差分
        
        # 変化が小さいピクセルは前のフレームのピクセルを使用
        # これによりGIFの差分圧縮が効果的に機能する
        result_array = curr_array.copy()
        unchanged_mask = pixel_diff <= tolerance
        result_array[unchanged_mask] = prev_array[unchanged_mask]
        
        return Image.fromarray(result_array.astype('uint8'), 'RGB')
    
    @staticmethod
    def optimize_gif_frames(frames: List[Image.Image], 
                          tolerance: int = 3) -> List[Image.Image]:
        """フレームリストを差分合成用に最適化"""
        
        if not frames:
            return []
        
        optimized_frames = []
        previous_frame = None
        
        for i, frame in enumerate(frames):
            # 全てRGBに統一
            frame_rgb = frame.convert('RGB')
            
            if i == 0:
                # 最初のフレームはそのまま
                optimized_frames.append(frame_rgb)
                previous_frame = frame_rgb
            else:
                # 差分フレームを生成（変化の少ない部分は前フレームと同じ色に）
                diff_frame = GifOptimizationService.create_frame_difference(
                    previous_frame, frame_rgb, tolerance
                )
                optimized_frames.append(diff_frame)
                previous_frame = frame_rgb
        
        return optimized_frames
    
    @staticmethod
    def save_optimized_gif(frames: List[Image.Image],
                         output_path: str,
                         duration: int = 100,
                         loop: int = 0,
                         tolerance: int = 3) -> Tuple[bool, Optional[int]]:
        """差分合成最適化されたGIFを保存"""
        
        if not frames:
            return False, None
        
        try:
            # フレームを差分合成用に最適化
            optimized_frames = GifOptimizationService.optimize_gif_frames(frames, tolerance)
            
            # より効果的なGIF保存オプション
            save_kwargs = {
                'save_all': True,
                'append_images': optimized_frames[1:],
                'duration': duration,
                'loop': loop,
                'optimize': True,  # 重要：ファイルサイズ最適化
                'disposal': 0,     # フレームを保持（差分に最適）
            }
            
            # パレット数を制限してファイルサイズを削減
            first_frame = optimized_frames[0]
            if hasattr(first_frame, 'quantize'):
                # 256色以下に制限
                first_frame = first_frame.quantize(colors=128, method=Image.MEDIANCUT, dither=0)
                optimized_frames = [first_frame] + [
                    frame.quantize(colors=128, method=Image.MEDIANCUT, dither=0) 
                    for frame in optimized_frames[1:]
                ]
                save_kwargs['palette'] = first_frame.getpalette()
            
            # GIFを保存
            optimized_frames[0].save(output_path, format='GIF', **save_kwargs)
            
            # ファイルサイズを返す
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Optimized GIF saved: {output_path} ({file_size:,} bytes)")
                return True, file_size
            else:
                return False, None
        
        except Exception as e:
            logger.error(f"GIF optimization failed: {str(e)}")
            return False, None
    
    @staticmethod
    def calculate_compression_ratio(original_size: int, optimized_size: int) -> float:
        """圧縮率を計算"""
        if original_size == 0:
            return 0.0
        return ((original_size - optimized_size) / original_size) * 100
    
    @staticmethod
    def get_optimization_stats(frames: List[Image.Image], 
                             tolerance: int = 3) -> dict:
        """最適化統計情報を取得"""
        if not frames:
            return {}
        
        try:
            optimized_frames = GifOptimizationService.optimize_gif_frames(frames, tolerance)
            
            # 変更ピクセル数の統計
            total_pixels = frames[0].width * frames[0].height
            changed_pixels_stats = []
            
            for i in range(1, len(frames)):
                prev_array = np.array(frames[i-1].convert('RGB'))
                curr_array = np.array(frames[i].convert('RGB'))
                
                diff = np.abs(prev_array.astype(int) - curr_array.astype(int))
                pixel_diff = np.max(diff, axis=2)
                
                changed_pixels = np.sum(pixel_diff > tolerance)
                change_ratio = (changed_pixels / total_pixels) * 100
                
                changed_pixels_stats.append({
                    'frame': i,
                    'changed_pixels': int(changed_pixels),
                    'change_ratio': float(change_ratio)
                })
            
            avg_change_ratio = np.mean([stat['change_ratio'] for stat in changed_pixels_stats])
            
            return {
                'total_frames': len(frames),
                'total_pixels_per_frame': total_pixels,
                'tolerance': tolerance,
                'average_change_ratio': float(avg_change_ratio),
                'frame_stats': changed_pixels_stats
            }
        
        except Exception as e:
            logger.error(f"Stats calculation failed: {str(e)}")
            return {}


# グローバルサービスインスタンス
gif_optimization_service = GifOptimizationService()
