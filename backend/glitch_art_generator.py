import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import colorsys
from typing import Tuple, List, Optional
import math

class GlitchArtGenerator:
    """グリッチアート風のピクセルアートを生成するクラス"""
    
    def __init__(self, width: int = 512, height: int = 512):
        self.width = width
        self.height = height
        self.pixel_size = 4  # ピクセルアート感を出すためのサイズ
        
        # ネオンカラーパレット
        self.neon_colors = [
            (255, 0, 255),    # ネオンピンク
            (0, 255, 255),    # シアン
            (255, 255, 0),    # イエロー
            (255, 0, 128),    # ホットピンク
            (128, 0, 255),    # パープル
            (0, 255, 128),    # ミントグリーン
            (255, 128, 0),    # オレンジ
            (255, 64, 64),    # レッド
        ]
        
    def create_base_image(self) -> Image.Image:
        """黒背景のベース画像を作成"""
        return Image.new('RGB', (self.width, self.height), (0, 0, 0))
    
    def add_glitch_lines(self, img: Image.Image, density: float = 0.1) -> Image.Image:
        """グリッチ風の歪んだ線を追加"""
        draw = ImageDraw.Draw(img)
        
        for _ in range(int(self.height * density)):
            y = random.randint(0, self.height - 1)
            x_start = random.randint(0, self.width // 2)
            x_end = random.randint(self.width // 2, self.width)
            
            # 線の歪み
            distortion = random.randint(-20, 20)
            color = random.choice(self.neon_colors)
            
            # ピクセル化された線
            for x in range(x_start, x_end, self.pixel_size):
                y_offset = int(math.sin(x * 0.1) * distortion)
                y_pos = y + y_offset
                if 0 <= y_pos < self.height:
                    draw.rectangle(
                        [x, y_pos, x + self.pixel_size, y_pos + self.pixel_size],
                        fill=color
                    )
        
        return img
    
    def add_geometric_patterns(self, img: Image.Image) -> Image.Image:
        """幾何学的パターンを追加"""
        draw = ImageDraw.Draw(img)
        
        # 円形パターン
        for _ in range(random.randint(2, 5)):
            center_x = random.randint(100, self.width - 100)
            center_y = random.randint(100, self.height - 100)
            radius = random.randint(50, 150)
            color = random.choice(self.neon_colors)
            
            # 同心円を描く
            for r in range(0, radius, self.pixel_size * 2):
                # ピクセル化された円
                self._draw_pixelated_circle(draw, center_x, center_y, r, color)
        
        # 四角形パターン
        for _ in range(random.randint(1, 3)):
            x = random.randint(50, self.width - 150)
            y = random.randint(50, self.height - 150)
            size = random.randint(50, 100)
            color = random.choice(self.neon_colors)
            
            # ピクセル化された四角形
            self._draw_pixelated_rectangle(draw, x, y, size, size, color)
        
        return img
    
    def add_ascii_elements(self, img: Image.Image) -> Image.Image:
        """アスキーアート風の要素を追加"""
        draw = ImageDraw.Draw(img)
        
        # アスキー文字のパターン
        ascii_chars = ['=', '-', '+', '*', '#', '@', '/', '\\', '|', '_']
        
        for _ in range(random.randint(5, 15)):
            char = random.choice(ascii_chars)
            x = random.randint(0, self.width - 50)
            y = random.randint(0, self.height - 50)
            color = random.choice(self.neon_colors)
            
            # 文字列を繰り返す
            text = char * random.randint(3, 8)
            
            # ピクセルフォント風に描画（簡易版）
            for i, c in enumerate(text):
                draw.rectangle(
                    [x + i * self.pixel_size, y, 
                     x + (i + 1) * self.pixel_size, y + self.pixel_size],
                    fill=color
                )
        
        return img
    
    def add_noise_pattern(self, img: Image.Image, intensity: float = 0.1) -> Image.Image:
        """ノイズパターンを追加"""
        pixels = img.load()
        
        for _ in range(int(self.width * self.height * intensity / 100)):  # intensityを調整
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # ピクセル単位でノイズを追加
            if random.random() > 0.7:  # より少ないノイズ
                color = random.choice(self.neon_colors)
                # ピクセルサイズに合わせて描画
                px_start = (x // self.pixel_size) * self.pixel_size
                py_start = (y // self.pixel_size) * self.pixel_size
                for px in range(px_start, min(self.width, px_start + self.pixel_size)):
                    for py in range(py_start, min(self.height, py_start + self.pixel_size)):
                        pixels[px, py] = color
        
        return img
    
    def add_scan_lines(self, img: Image.Image) -> Image.Image:
        """スキャンライン効果を追加"""
        draw = ImageDraw.Draw(img)
        
        for y in range(0, self.height, self.pixel_size * 2):
            if random.random() > 0.7:  # ランダムにスキップ
                continue
                
            # 半透明の線を描画
            color = (*random.choice(self.neon_colors), 64)  # アルファ値を追加
            draw.rectangle([0, y, self.width, y + 1], fill=color[:3])
        
        return img
    
    def _draw_pixelated_circle(self, draw: ImageDraw.Draw, cx: int, cy: int, 
                              radius: int, color: Tuple[int, int, int]):
        """ピクセル化された円を描画"""
        for angle in range(0, 360, 5):
            x = int(cx + radius * math.cos(math.radians(angle)))
            y = int(cy + radius * math.sin(math.radians(angle)))
            
            # ピクセル単位で描画
            x = (x // self.pixel_size) * self.pixel_size
            y = (y // self.pixel_size) * self.pixel_size
            
            draw.rectangle(
                [x, y, x + self.pixel_size, y + self.pixel_size],
                fill=color
            )
    
    def _draw_pixelated_rectangle(self, draw: ImageDraw.Draw, x: int, y: int,
                                 width: int, height: int, color: Tuple[int, int, int]):
        """ピクセル化された四角形を描画"""
        # 枠線のみ描画
        for i in range(0, width, self.pixel_size):
            # 上辺
            draw.rectangle(
                [x + i, y, x + i + self.pixel_size, y + self.pixel_size],
                fill=color
            )
            # 下辺
            draw.rectangle(
                [x + i, y + height - self.pixel_size, 
                 x + i + self.pixel_size, y + height],
                fill=color
            )
        
        for i in range(0, height, self.pixel_size):
            # 左辺
            draw.rectangle(
                [x, y + i, x + self.pixel_size, y + i + self.pixel_size],
                fill=color
            )
            # 右辺
            draw.rectangle(
                [x + width - self.pixel_size, y + i, 
                 x + width, y + i + self.pixel_size],
                fill=color
            )
    
    def generate(self, style: str = "full") -> Image.Image:
        """グリッチアートを生成"""
        img = self.create_base_image()
        
        if style == "full" or style == "lines":
            img = self.add_glitch_lines(img, density=0.1)
        
        if style == "full" or style == "geometric":
            img = self.add_geometric_patterns(img)
        
        if style == "full" or style == "ascii":
            img = self.add_ascii_elements(img)
        
        if style == "full" or style == "noise":
            img = self.add_noise_pattern(img, intensity=0.05)
        
        if style == "full":
            img = self.add_scan_lines(img)
        
        return img
    
    def generate_animated_frames(self, frames: int = 8) -> List[Image.Image]:
        """アニメーション用のフレームを生成"""
        animation_frames = []
        
        base_seed = random.randint(0, 10000)
        
        for frame in range(frames):
            # 各フレームで異なるシードを使用
            random.seed(base_seed + frame)
            frame_img = self.generate()
            animation_frames.append(frame_img)
        
        return animation_frames
