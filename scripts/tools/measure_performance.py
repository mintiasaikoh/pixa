#!/usr/bin/env python3
"""
最適化効果測定スクリプト
"""
import time
import psutil
import requests
import json
import sys

print("🔍 Pixa最適化効果測定")
print("=" * 50)

# サーバーが起動するまで待機
print("\nサーバー起動を待機中...")
for i in range(30):
    try:
        response = requests.get("http://localhost:5001/health")
        if response.status_code == 200:
            print("✅ サーバー起動確認")
            break
    except:
        pass
    time.sleep(1)
else:
    print("❌ サーバー起動タイムアウト")
    sys.exit(1)

# 初期メモリ使用量
process = psutil.Process()
initial_memory = process.memory_info().rss / 1024 / 1024

print(f"\n📊 初期メモリ使用量: {initial_memory:.1f} MB")

# テスト生成
test_params = {
    "prompt": "pixelsprite, test character",
    "model_id": "runwayml/stable-diffusion-v1-5",
    "width": 512,
    "height": 512,
    "pixel_size": 8,
    "palette_size": 16,
    "steps": 20,
    "guidance_scale": 7.5
}

print("\n⏱️ 生成速度テスト中...")
times = []

for i in range(3):
    start = time.time()
    response = requests.post("http://localhost:5001/generate", json=test_params)
    end = time.time()
    
    if response.status_code == 200:
        times.append(end - start)
        print(f"  テスト{i+1}: {times[-1]:.2f}秒")
    else:
        print(f"  テスト{i+1}: エラー")

if times:
    avg_time = sum(times) / len(times)
    print(f"\n平均生成時間: {avg_time:.2f}秒")

# 最終メモリ使用量
final_memory = process.memory_info().rss / 1024 / 1024
memory_increase = final_memory - initial_memory

print(f"\n📊 最終メモリ使用量: {final_memory:.1f} MB")
print(f"   メモリ増加: {memory_increase:.1f} MB")

print("\n✅ 測定完了")
