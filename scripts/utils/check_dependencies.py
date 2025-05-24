#!/usr/bin/env python3
"""
基本的な動作確認テスト
"""

import sys

print("Python動作確認...")
print(f"Pythonバージョン: {sys.version}")

try:
    import flask
    print("✓ Flask")
except ImportError:
    print("✗ Flask - インストールが必要です")

try:
    import torch
    print(f"✓ PyTorch - MPS利用可能: {torch.backends.mps.is_available()}")
except ImportError:
    print("✗ PyTorch - インストールが必要です")

try:
    import diffusers
    print("✓ Diffusers")
except ImportError:
    print("✗ Diffusers - インストールが必要です")

try:
    import imageio
    print("✓ imageio")
    
    # GIF作成テスト
    import numpy as np
    from PIL import Image
    import io
    
    # テスト画像作成
    frames = []
    for i in range(4):
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[:, :, 0] = i * 60  # 赤色のグラデーション
        img = Image.fromarray(arr)
        frames.append(np.array(img))    
    # GIF作成
    gif_buffer = io.BytesIO()
    imageio.mimsave(gif_buffer, frames, format='GIF', duration=100)
    print("  → GIF作成テスト成功")
    
except ImportError:
    print("✗ imageio - インストールが必要です")
except Exception as e:
    print(f"✗ imageio - エラー: {e}")

try:
    import pygame
    print("✓ pygame")
except ImportError:
    print("✗ pygame - インストールが必要です")

print("\n依存関係チェック完了")