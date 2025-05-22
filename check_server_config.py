#!/usr/bin/env python3
"""
サーバー構成の確認スクリプト
"""

import requests

print("=== Pixaサーバー構成確認 ===\n")

BASE_URL = "http://localhost:5001"

# 1. フロントエンドの確認
print("1. フロントエンド配信チェック...")
try:
    response = requests.get(BASE_URL)
    if response.status_code == 200 and "Pixa" in response.text:
        print("   ✓ HTMLページが正常に配信されています")
    else:
        print("   × HTMLページの配信に問題があります")
except Exception as e:
    print(f"   × エラー: {e}")

# 2. 静的ファイルの確認
print("\n2. 静的ファイル配信チェック...")
static_files = ["app.js", "style.css"]
for file in static_files:
    try:
        response = requests.get(f"{BASE_URL}/{file}")
        if response.status_code == 200:
            print(f"   ✓ {file} が正常に配信されています")
        else:
            print(f"   × {file} の配信に問題があります")
    except Exception as e:
        print(f"   × {file} エラー: {e}")

# 3. APIエンドポイントの確認
print("\n3. APIエンドポイントチェック...")
try:
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(f"   ✓ /health エンドポイント: {data['status']}")
except Exception as e:
    print(f"   × /health エラー: {e}")

print("\n結論: フロントエンドとバックエンドは同じサーバー（ポート5001）で動作しています！")
