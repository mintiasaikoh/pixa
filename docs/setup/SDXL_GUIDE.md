# SDXLピクセルアートモデル使用ガイド

## 新しく追加されたSDXLモデル

### 1. Pixel Art XL LoRA（nerijs/pixel-art-xl）

**特徴**:
- 超高速生成：わずか8ステップで生成可能
- 高解像度：1024x1024の美しいピクセルアート
- LCMスケジューラーによる最適化

**使用例**:
```
プロンプト: pixel, a cyberpunk cat hacker with neon glasses
ネガティブプロンプト: 3d render, realistic
```

**推奨設定**:
- ステップ数: 8
- ガイダンススケール: 1.5
- 解像度: 1024x1024

### 2. Pixel Party XL（pixelparty/pixel-party-xl）

**特徴**:
- インディーゲーム開発に最適
- 小さいアイテムやキャラクターの生成が得意
- フルモデルトレーニングによる高品質

**使用例**:
```
プロンプト: a treasure chest with golden coins. in pixel art style
ネガティブプロンプト: （不要）
```

**推奨設定**:
- ステップ数: 25
- ガイダンススケール: 7.5
- 解像度: 512x512（128x128も可）

## プロンプトのコツ

### nerijs/pixel-art-xl の場合
- 必ず「pixel」をプロンプトの最初に追加
- シンプルで明確な説明が効果的
- 例：
  - ✅ `pixel, magical sword with blue flames`
  - ❌ `a magical sword with blue flames pixel art`

### pixelparty/pixel-party-xl の場合
- プロンプトの最後に「. in pixel art style」を追加
- より詳細な説明が可能
- 例：
  - ✅ `ancient temple covered in vines. in pixel art style`
  - ❌ `pixel art ancient temple`

## SDXLモデルの利点

1. **高解像度**: 1024x1024の詳細なピクセルアート
2. **高速生成**: LoRA版は8ステップで生成可能
3. **品質**: より洗練されたピクセルアート表現
4. **柔軟性**: 様々なスタイルに対応

## トラブルシューティング

### メモリ不足エラーが出る場合
- 解像度を512x512に下げる
- バッチサイズを1にする
- float16精度を使用（自動設定済み）

### 生成が遅い場合
- nerijs/pixel-art-xlを使用（8ステップで高速）
- M2 ProのMPS最適化を確認

### ピクセルアート感が弱い場合
- pixel_sizeパラメータを大きくする（8-16）
- palette_sizeを小さくする（8-16）

## 実装の技術詳細

### LoRAの読み込み（nerijs/pixel-art-xl）
```python
# ベースモデル（SDXL）を読み込み
pipeline = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
)

# LCMスケジューラーを設定
pipeline.scheduler = LCMScheduler.from_config(pipeline.scheduler.config)

# LoRAを読み込み
pipeline.load_lora_weights("latent-consistency/lcm-lora-sdxl", adapter_name="lcm")
pipeline.load_lora_weights("nerijs/pixel-art-xl", adapter_name="pixel")

# アダプターを設定
pipeline.set_adapters(["lcm", "pixel"], adapter_weights=[1.0, 1.2])
```

### UNetのみの置き換え（pixelparty/pixel-party-xl）
```python
# UNetのみを読み込み
unet = UNet2DConditionModel.from_pretrained(
    "pixelparty/pixel-party-xl",
    torch_dtype=torch.float16
)

# ベースパイプラインに組み込み
pipeline = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    unet=unet,
    torch_dtype=torch.float16
)
```

これらの実装により、Civitaiの「Pixel Art Diffusion XL」と同等以上の高品質なピクセルアート生成が可能になりました！
