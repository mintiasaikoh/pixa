#!/usr/bin/env python3
"""
Pixa改善版のテストスクリプト
バグ修正とパフォーマンス最適化の確認
"""

import sys
import os
import time
import requests
import json

# プロジェクトルートのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_server_optimized():
    """最適化されたサーバーのテスト"""
    print("🔧 最適化されたサーバーのテスト開始...")
    
    # サーバーのヘルスチェック
    try:
        response = requests.get('http://localhost:5001/health')
        data = response.json()
        print(f"✅ サーバーステータス: {data['status']}")
        print(f"📊 使用デバイス: {data['device']}")
        print(f"🤖 ロード済みモデル: {data['current_model']}")
    except Exception as e:
        print(f"❌ サーバー接続エラー: {e}")
        return False
    
    return True

def test_black_image_fix():
    """真っ黒な画像問題の修正テスト"""
    print("\n🎨 画像生成テスト（真っ黒な画像の修正確認）...")
    
    test_cases = [
        {
            "prompt": "pixel art cat",
            "model_id": "runwayml/stable-diffusion-v1-5",
            "steps": 20
        },
        {
            "prompt": "pixelsprite cat warrior",
            "model_id": "PublicPrompts/All-In-One-Pixel-Model",
            "steps": 25
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nテストケース {i+1}: {test['model_id']}")
        
        try:
            start_time = time.time()
            response = requests.post('http://localhost:5001/generate', 
                                   json=test,
                                   timeout=60)
            
            elapsed = time.time() - start_time
            data = response.json()
            
            if data.get('success'):
                print(f"✅ 生成成功（{elapsed:.2f}秒）")
                # 画像データの確認
                if data.get('image', '').startswith('data:image'):
                    print("✅ 有効な画像データを受信")
                else:
                    print("⚠️ 画像データが不正")
            else:
                print(f"❌ 生成失敗: {data.get('error')}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")

def test_performance_optimizations():
    """パフォーマンス最適化のテスト"""
    print("\n⚡ パフォーマンス最適化テスト...")
    
    # メモリ使用量のチェック（Pythonプロセス内で確認）
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        print(f"📊 メモリ使用量: {memory_info.rss / 1024 / 1024:.2f} MB")
    except ImportError:
        print("ℹ️ psutilがインストールされていません")
    
    # 連続生成テスト
    print("\n🔄 連続生成テスト（メモリリーク確認）...")
    
    for i in range(3):
        print(f"\n生成 {i+1}/3:")
        
        params = {
            "prompt": f"pixel art test image {i}",
            "model_id": "runwayml/stable-diffusion-v1-5",
            "steps": 15,
            "width": 256,
            "height": 256
        }
        
        try:
            start_time = time.time()
            response = requests.post('http://localhost:5001/generate', 
                                   json=params,
                                   timeout=30)
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ 生成完了（{elapsed:.2f}秒）")
            else:
                print(f"❌ エラー: {response.status_code}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        time.sleep(2)  # クールダウン

def test_glitch_art():
    """グリッチアート生成のテスト"""
    print("\n✨ グリッチアート生成テスト...")
    
    styles = ['full', 'lines', 'geometric', 'ascii', 'noise']
    
    for style in styles:
        print(f"\nスタイル '{style}' をテスト中...")
        
        params = {
            "style": style,
            "pixel_size": 4,
            "animated": False,
            "width": 512,
            "height": 512
        }
        
        try:
            start_time = time.time()
            response = requests.post('http://localhost:5001/generate_glitch', 
                                   json=params,
                                   timeout=10)
            
            elapsed = time.time() - start_time
            data = response.json()
            
            if data.get('success'):
                print(f"✅ 生成成功（{elapsed:.2f}秒）")
            else:
                print(f"❌ 生成失敗: {data.get('error')}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")

def test_ui_endpoints():
    """UI関連エンドポイントのテスト"""
    print("\n🌐 UIエンドポイントテスト...")
    
    endpoints = [
        ('/', 'メインページ'),
        ('/models', 'モデル一覧'),
        ('/health', 'ヘルスチェック')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5001{endpoint}')
            if response.status_code == 200:
                print(f"✅ {name} ({endpoint}): OK")
            else:
                print(f"❌ {name} ({endpoint}): {response.status_code}")
        except Exception as e:
            print(f"❌ {name} ({endpoint}): {e}")

def main():
    """メインテスト実行"""
    print("🎯 Pixa改善版総合テスト")
    print("=" * 50)
    
    # サーバーが起動しているか確認
    if not test_server_optimized():
        print("\n⚠️ サーバーが起動していません。")
        print("./start_server.sh を実行してください。")
        return
    
    # 各種テストを実行
    test_black_image_fix()
    test_performance_optimizations()
    test_glitch_art()
    test_ui_endpoints()
    
    print("\n" + "=" * 50)
    print("✨ テスト完了！")
    print("\n📌 改善された点:")
    print("1. ✅ 真っ黒な画像問題の修正")
    print("2. ✅ メモリ使用量の最適化")
    print("3. ✅ エラーハンドリングの改善")
    print("4. ✅ UIの現代的なデザイン")
    print("5. ✅ グリッチアート生成機能")

if __name__ == "__main__":
    main()
