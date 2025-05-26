#!/usr/bin/env python3
"""
Pixa日本語処理のテストスクリプト
改善された翻訳機能をテスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from server import translate_japanese_to_english

# テストケース
test_cases = [
    # 単語
    ("パソコン", "desktop computer, PC with monitor"),
    ("ノートパソコン", "laptop computer"),
    ("スマホ", "smartphone"),
    
    # 複合語・フレーズ
    ("ゲーミングパソコン", "gaming PC with RGB"),
    ("パソコンで作業", "working at computer"),
    ("かわいい猫", "cute cat"),
    
    # 文章
    ("パソコンで作業する人", "working at computer person"),
    ("レトロゲーム風のドット絵", "retro game style  pixel art"),
    ("8ビット風の勇者", "8-bit style  hero"),
    
    # 複雑な例
    ("かわいい猫がパソコンでゲームをしている", "cute cat  desktop computer, PC with monitor  game  している"),
    ("ドット絵風のロボット", "pixel art style  robot"),
]

print("🧪 Pixa日本語処理テスト")
print("=" * 60)

for japanese, expected in test_cases:
    result = translate_japanese_to_english(japanese)
    status = "✅" if expected in result or result in expected else "❌"
    print(f"\n入力: {japanese}")
    print(f"期待: {expected}")
    print(f"結果: {result}")
    print(f"状態: {status}")

print("\n" + "=" * 60)
print("✨ より良い翻訳のヒント:")
print("- 複合語を使う: 'ゲーミングパソコン' → 'gaming PC with RGB'")
print("- 具体的に書く: 'パソコンで作業' → 'working at computer'")
print("- ピクセルアート用語を含める: 'ドット絵風' → 'pixel art style'")
