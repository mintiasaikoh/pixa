#!/usr/bin/env python3
import requests
import json
import base64
from datetime import datetime
import os

# APIエンドポイント
url = "http://localhost:5001/generate_animation"

# リクエストデータ
data = {
    "prompt": "横向きの猫がパソコンの画面を見つめている、座っている猫、デスクに座る猫",
    "animation_type": "idle",  # 微妙に動くアイドルアニメーション
    "frame_count": 8,  # 8フレーム
    "fps": 10,  # 10FPS
    "pixel_size": 8,
    "palette_size": 32,
    "steps": 20,
    "negative_prompt": "正面向き、後ろ向き、ぼやけた、低品質"
}

print("🎨 アニメーションGIF生成中...")
print(f"プロンプト: {data['prompt']}")
print(f"アニメーションタイプ: {data['animation_type']}")
print(f"フレーム数: {data['frame_count']}")
print(f"FPS: {data['fps']}")
print(f"ピクセルサイズ: {data['pixel_size']}px")
print(f"色数: {data['palette_size']}色")

try:
    # APIリクエスト送信
    response = requests.post(url, json=data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            # Base64画像データの処理
            image_data_base64 = result['image']
            
            # データURLフォーマットの場合
            if image_data_base64.startswith('data:image'):
                # data:image/gif;base64, を削除
                image_data_base64 = image_data_base64.split(',')[1]
            
            # パディングを修正
            missing_padding = len(image_data_base64) % 4
            if missing_padding:
                image_data_base64 += '=' * (4 - missing_padding)
            
            # デコード
            image_data = base64.b64decode(image_data_base64)
            
            # ファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cat_computer_side_{timestamp}.gif"
            filepath = f"/Users/mymac/pixa/{filename}"
            
            # GIFを保存
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ GIF生成成功！")
            print(f"ファイル: {filepath}")
            print(f"メッセージ: {result.get('message', '')}")
            
            # macOSで画像を開く
            os.system(f'open "{filepath}"')
        else:
            print("❌ エラー: 生成に失敗しました")
            print(result)
        
    else:
        print(f"❌ エラー: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ エラーが発生しました: {str(e)}")
    import traceback
    traceback.print_exc()
