#!/usr/bin/env python3
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PILがインストールされていないため、デフォルトアイコンを使用します")
    sys.exit(0)

# アイコン画像を作成（512x512）
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 背景（角丸四角形）
def draw_rounded_rect(draw, coords, radius, fill):
    x1, y1, x2, y2 = coords
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+2*radius, y1+2*radius], 180, 270, fill=fill)
    draw.pieslice([x2-2*radius, y1, x2, y1+2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*radius, x1+2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*radius, y2-2*radius, x2, y2], 0, 90, fill=fill)

# 背景グラデーション
draw_rounded_rect(draw, [20, 20, 492, 492], 50, '#1a1a1a')

# ピクセルアートパターン
pixel_size = 24
colors = ['#00ff41', '#ff0080', '#ffff00', '#00b8ff']
pattern = [
    [0, 1, 1, 0, 0, 2, 2, 0],
    [1, 0, 0, 1, 2, 0, 0, 2],
    [1, 0, 0, 1, 2, 0, 0, 2],
    [0, 1, 1, 0, 0, 2, 2, 0],
    [3, 0, 0, 3, 0, 1, 1, 0],
    [0, 3, 3, 0, 1, 0, 0, 1],
    [0, 3, 3, 0, 1, 0, 0, 1],
    [3, 0, 0, 3, 0, 1, 1, 0]
]

# パターンを中央に配置
start_x = size // 2 - len(pattern[0]) * pixel_size // 2
start_y = size // 2 - len(pattern) * pixel_size // 2

for y, row in enumerate(pattern):
    for x, color_idx in enumerate(row):
        if color_idx > 0:
            color = colors[color_idx - 1]
            draw.rectangle([
                start_x + x * pixel_size,
                start_y + y * pixel_size,
                start_x + (x + 1) * pixel_size - 2,
                start_y + (y + 1) * pixel_size - 2
            ], fill=color)

# "PIXA"テキスト（ピクセルフォント風）
text_y = start_y + len(pattern) * pixel_size + 40
text = "PIXA"
text_size = 48
for i, char in enumerate(text):
    x = size // 2 - len(text) * text_size // 2 + i * text_size
    # 簡易的なピクセルフォント
    draw.rectangle([x, text_y, x + text_size - 8, text_y + text_size], fill='#00ff41')

# 画像を保存
img.save('pixa_icon_512.png')

# 各サイズのアイコンを作成
sizes = [512, 256, 128, 64, 32, 16]
os.makedirs('pixa.iconset', exist_ok=True)

for s in sizes:
    resized = img.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(f'pixa.iconset/icon_{s}x{s}.png')
    # Retinaディスプレイ用
    if s <= 256:
        resized_2x = img.resize((s*2, s*2), Image.Resampling.LANCZOS)
        resized_2x.save(f'pixa.iconset/icon_{s}x{s}@2x.png')

print("✅ アイコンファイルが作成されました")
