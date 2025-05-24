# モデルのダウンロード方法

## 🚀 クイックスタート

```bash
# モデルをダウンロード
python download_models.py

# または
./download_models.py
```

## 📦 ダウンロードオプション

1. **必須モデルのみ（約6GB）**
   - Stable Diffusion v1.5
   - All-In-One Pixel Model

2. **推奨モデル（約7GB）**
   - 上記 + SDXL Base + LoRA

3. **全モデル（約25GB）**
   - すべてのモデル

4. **カスタム選択**
   - 必要なモデルだけを選択

## 💾 保存場所

モデルは以下に保存されます：
- `~/.cache/huggingface/hub/`

## ⚡ 注意事項

- 初回ダウンロードには時間がかかります
- 安定したインターネット接続が必要です
- 中断しても再開可能（レジューム機能付き）

## 🎨 モデル一覧

| モデル | サイズ | 用途 |
|--------|--------|------|
| SD 1.5 | ~4GB | 基本モデル |
| All-In-One | ~2GB | ピクセルアート特化（推奨） |
| Sprite Sheet | ~2GB | 4方向スプライト |
| Pixel Art Style | ~2GB | シンプルなスタイル |
| Analog Diffusion | ~2GB | レトロ風 |
| SDXL Base | ~7GB | 高解像度用ベース |
| Pixel Art XL LoRA | ~200MB | 高速・高品質 |
| LCM LoRA | ~200MB | 8ステップ生成 |
| Pixel Party XL | ~5GB | インディーゲーム向け |
