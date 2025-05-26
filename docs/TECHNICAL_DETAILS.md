# 🔧 Pixa 技術詳細ドキュメント

## アーキテクチャ

```
pixa/
├── backend/                      # Pythonバックエンド
│   ├── server.py                # メインサーバー
│   ├── pixa_japanese_processor.py # 日本語処理
│   ├── pixa_japanese_dict.py    # 日本語辞書
│   ├── creative_animations.py   # アニメーション生成
│   ├── glitch_art_generator.py  # グリッチアート
│   └── requirements.txt         # Python依存関係
│
├── frontend/                    # Web UI
│   ├── index.html              # 統合UI
│   ├── unified-ui.css          # 統合UIスタイル
│   ├── unified-settings.js     # アコーディオン機能
│   ├── modern-app.js           # アプリケーションロジック
│   ├── modern-ui.css           # モダンUIスタイル
│   └── app.js                  # pygame版用
│
├── models/                     # AIモデル（自動ダウンロード）
├── scripts/                    # ユーティリティスクリプト
├── docs/                       # ドキュメント
│
├── start_server.sh            # 起動スクリプト
├── stop_server.sh             # 停止スクリプト
└── README.md                  # メインドキュメント
```

## 使用技術スタック

### バックエンド
- **Python 3.8+** - メイン言語
- **Flask** - Webフレームワーク
- **PyTorch** - 深層学習フレームワーク
- **Diffusers** - Stable Diffusion実装
- **Pillow** - 画像処理
- **NumPy** - 数値計算

### フロントエンド
- **HTML5/CSS3** - マークアップ
- **JavaScript (ES6+)** - インタラクティブ機能
- **Bootstrap 5** - UIフレームワーク
- **Font Awesome** - アイコン

### AIモデル
- **Stable Diffusion v1.5** - ベースモデル
- **PublicPrompts/All-In-One-Pixel-Model** - ピクセルアート特化

## 最適化技術

### Apple Silicon (M1/M2) 最適化
```python
# Metal Performance Shaders (MPS) を使用
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# メモリ最適化
pipe.enable_attention_slicing(slice_size=1)
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()
```

### メモリ管理
- 使用後の自動メモリクリーンアップ
- バッチサイズの動的調整
- 不要なテンソルの即座解放

## API エンドポイント

### POST /generate
画像生成のメインエンドポイント

**リクエスト:**
```json
{
  "prompt": "ファミコン風8ビットピクセルアート",
  "negative_prompt": "ぼやけた, 低品質",
  "model": "PublicPrompts/All-In-One-Pixel-Model",
  "steps": 20,
  "cfg_scale": 7,
  "seed": -1,
  "pixel_size": 8,
  "palette_size": 16,
  "aspect_ratio": "1:1"
}
```

**レスポンス:**
```json
{
  "image": "base64エンコード画像",
  "seed": 12345,
  "model_used": "PublicPrompts/All-In-One-Pixel-Model"
}
```

### POST /generate_glitch_art
グリッチアート生成（AIなし）

### POST /animate
アニメーション生成

## パフォーマンス詳細

### 生成時間（M2 Pro）
| 画像サイズ | ステップ数 | 生成時間 |
|-----------|----------|---------|
| 256×256   | 20       | 5-8秒   |
| 512×512   | 20       | 10-15秒 |
| 768×768   | 30       | 20-30秒 |

### メモリ使用量
- 起動時: 約300MB
- モデル読み込み後: 約2GB
- 生成中: 約3-4GB

## 開発者向け情報

### デバッグモード
```bash
cd backend
python server.py --debug
```

### テスト実行
```bash
# 日本語翻訳テスト
python scripts/test_japanese_translation.py

# アニメーション生成テスト
python scripts/test_creative_animations.py

# グリッチアートテスト
python scripts/test_glitch_art.py
```

### 新機能追加時の注意点
1. `backend/server.py` に新しいエンドポイントを追加
2. `frontend/modern-app.js` にUI処理を追加
3. 必要に応じて `unified-settings.js` に設定を追加
4. ドキュメントを更新

## トラブルシューティング（詳細）

### MPSエラー
```python
# MPSが使用できない場合の対処
if not torch.backends.mps.is_available():
    print("MPS not available, falling back to CPU")
    device = torch.device("cpu")
```

### メモリ不足
```python
# メモリ使用量を削減
torch.cuda.empty_cache()  # CUDA用
gc.collect()  # Python GC
```

### モデル読み込みエラー
```bash
# モデルキャッシュをクリア
rm -rf ~/.cache/huggingface/
```