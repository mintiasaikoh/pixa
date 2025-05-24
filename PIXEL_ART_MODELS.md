# ピクセルアート特化モデル実装ガイド

## 実装済みモデル

### SD 1.5ベースモデル

#### 1. PublicPrompts/All-In-One-Pixel-Model（推奨）
- **特徴**: キャラクターと背景の両方に対応
- **トリガーワード**: 
  - `pixelsprite`: キャラクター用
  - `16bitscene`: 背景用

#### 2. Onodofthenorth/SD_PixelArt_SpriteSheet_Generator
- **特徴**: 4方向のスプライトシート生成に特化
- **トリガーワード**:
  - `PixelartFSS`: 前向き
  - `PixelartRSS`: 右向き
  - `PixelartBSS`: 後ろ向き
  - `PixelartLSS`: 左向き
- **特別機能**: 「4方向スプライトシートを生成」ボタンが表示される

#### 3. kohbanye/pixel-art-style
- **特徴**: シンプルで綺麗なピクセルアートスタイル
- **トリガーワード**: `pixelartstyle`

#### 4. wavymulder/Analog-Diffusion
- **特徴**: レトロ・アナログ風の雰囲気
- **トリガーワード**: `analog style`

### SDXL（高解像度）モデル

#### 5. nerijs/pixel-art-xl（LoRA）✨ NEW!
- **特徴**: SDXLベースの高解像度ピクセルアート
- **トリガーワード**: `pixel`
- **推奨設定**: 
  - ステップ数: 8（LCMスケジューラー使用）
  - ガイダンススケール: 1.5
  - 解像度: 1024x1024
- **高速生成**: LCM LoRAとの組み合わせで8ステップで生成可能

#### 6. pixelparty/pixel-party-xl 🎯 NEW!
- **特徴**: インディーゲーム開発向けに最適化
- **使用方法**: プロンプトの最後に `. in pixel art style` を追加
- **推奨設定**:
  - 解像度: 128x128が最適（512x512でも動作）
  - 小さいアイテムやキャラクターの生成に優れる

## Pixel Art Diffusion XLについて

Civitaiで人気の「Pixel Art Diffusion XL」の代わりに、Hugging Face上で以下の優れたSDXLベースのピクセルアートモデルを実装しました：

### 実装済みSDXLモデル

1. **nerijs/pixel-art-xl（LoRA）**
   - LCMスケジューラーとの組み合わせで超高速生成（8ステップ）
   - 高解像度（1024x1024）のピクセルアート生成が可能
   - トリガーワード「pixel」でシンプルに使用可能

2. **pixelparty/pixel-party-xl**
   - フルモデルトレーニングによる高品質な生成
   - インディーゲーム開発に特化
   - 小さいサイズ（128x128）から大きいサイズまで対応

### 使用方法

```python
# nerijs/pixel-art-xl の場合
prompt = "pixel, a cute dragon breathing fire"
negative_prompt = "3d render, realistic"

# pixelparty/pixel-party-xl の場合
prompt = "a magical forest with glowing mushrooms. in pixel art style"
```

## 新機能の使い方

### 1. モデル自動設定
- モデルを選択すると、推奨パラメータが自動的に設定されます
- トリガーワードの説明が表示されます

### 2. プロンプト自動最適化
- 各モデルに適したトリガーワードが自動追加されます
- 日本語プロンプトも自動翻訳されます

### 3. 4方向スプライトシート生成
- `Onodofthenorth/SD_PixelArt_SpriteSheet_Generator`選択時のみ
- 「4方向スプライトシートを生成」ボタンが表示
- 前・右・後・左の4方向を一度に生成

## 技術的な詳細

### backend/model_configs.py
- 各モデルの設定を一元管理
- トリガーワード、推奨設定、ネガティブプロンプトを定義

### backend/server.py
- `enhance_prompt_for_model()`: モデル固有のプロンプト最適化
- `enhance_negative_prompt_for_model()`: ネガティブプロンプト最適化
- `/generate_sprite_sheet`: 4方向スプライトシート生成エンドポイント
- `/models`: モデル情報を返すエンドポイント

### frontend/app.js
- `loadModels()`: 動的にモデル情報を取得
- `toggleSpriteSheetButton()`: モデルに応じたUI制御
- `generateSpriteSheet()`: 4方向スプライトシート生成

## トラブルシューティング

### モデルが読み込めない場合
1. モデルIDが正しいか確認
2. Hugging Faceのアクセストークンが必要な場合がある
3. モデルサイズによってはメモリ不足の可能性

### 生成が遅い場合
1. M2 ProのMPS最適化を確認
2. バッチサイズを小さくする
3. 解像度を下げる

### プロンプトが効かない場合
1. トリガーワードが正しく追加されているか確認
2. モデル固有の書式を確認
3. ネガティブプロンプトも調整

## 今後の拡張案

1. **LoRAサポート**: カスタムスタイルの追加
2. **タイルセット生成**: ゲーム用タイルの自動生成
3. **カラーパレット指定**: 特定のカラーパレットでの生成
4. **アニメーション補間**: より滑らかなアニメーション生成
