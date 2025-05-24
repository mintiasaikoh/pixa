#!/usr/bin/env python3
import requests
import json
import base64
from datetime import datetime
import os

# APIエンドポイント
url = "http://localhost:5001/generate"

# リクエストデータ
data = {
    "prompt": "かわいい猫がパソコンを触っている",
    "pixel_size": 8,
    "palette_size": 32,
    "steps": 20
}

print("🎨 ピクセルアート生成中...")
print(f"プロンプト: {data['prompt']}")
print(f"ピクセルサイズ: {data['pixel_size']}px")
print(f"色数: {data['palette_size']}色")

try:
    # APIリクエスト送信
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        # デバッグ情報
        print(f"レスポンスキー: {result.keys()}")
        
        if 'image' in result:
            # Base64画像データの処理
            image_data_base64 = result['image']
            
            # データURLフォーマットの場合
            if image_data_base64.startswith('data:image'):
                # data:image/png;base64, を削除
                image_data_base64 = image_data_base64.split(',')[1]
            
            # パディングを修正
            missing_padding = len(image_data_base64) % 4
            if missing_padding:
                image_data_base64 += '=' * (4 - missing_padding)
            
            # デコード
            image_data = base64.b64decode(image_data_base64)
            
            # ファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cat_computer_{timestamp}.png"
            filepath = f"/Users/mymac/pixa/{filename}"
            
            # 画像を保存
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ 生成成功！")
            print(f"ファイル: {filepath}")
            print(f"英語プロンプト: {result.get('english_prompt', 'N/A')}")
            
            # macOSで画像を開く
            os.system(f'open "{filepath}"')
        else:
            print("❌ エラー: 画像データが見つかりません")
            print(f"レスポンス: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    else:
        print(f"❌ エラー: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ エラーが発生しました: {str(e)}")
    import traceback
    traceback.print_exc()
