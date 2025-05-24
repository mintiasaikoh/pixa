# 🎨 Pixa - AI ピクセルアート ジェネレーター

M2 Pro Mac向けに最適化されたStable Diffusionベースのピクセルアート生成アプリケーションです。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-M1%2FM2-orange.svg)](https://support.apple.com/en-us/HT211814)

![AI Pixel Art Generator Demo](https://via.placeholder.com/800x400/333/fff?text=AI+Pixel+Art+Generator)

## 🎯 特徴

- **🍎 Apple Silicon (M2 Pro) 最適化**: Metal Performance Shaders (MPS) を活用した高速生成
- **🔒 完全ローカル実行**: クラウドサービス不要、プライバシー保護
- **🎮 ピクセルアート特化**: 自動的にピクセルアート風の後処理を適用
- **🎨 カラーパレット制限**: レトロゲーム風の色数制限機能
- **🌐 直感的なWeb UI**: モダンで使いやすいインターフェース
- **🖥️ デスクトップアプリ**: pygame版でネイティブデスクトップ体験
- **⚡ 高速生成**: 512×512px画像が約10-15秒
- **🇯🇵 日本語プロンプト対応**: 自動翻訳で日本語入力をサポート
- **🎯 複数のスタイルプリセット**: 8-bit、16-bit、ゲームボーイ風、ミニマル、高精細
- **🎬 アニメーション生成**: 静止画から動くGIFアニメーションを作成
- **🕹️ 4方向スプライトシート生成**: ゲーム開発向けの前後左右スプライト自動生成
- **🤖 複数のピクセルアート特化AIモデル**: 用途に応じて選択可能
- **📊 詳細パラメーター説明**: 各設定項目にわかりやすい説明文を表示

## 🚀 クイックスタート

### 1. 事前準備

以下がインストールされていることを確認してください：

- Python 3.8以上
- pip (Python package manager)
- 十分な空き容量（モデルファイル用に約10GB）

### 2. インストール

```bash
# リポジトリをクローン
git clone https://github.com/mintiasaikoh/pixa.git
cd pixa

# Python仮想環境を作成（推奨）
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r backend/requirements.txt
```

### 3. モデルのダウンロード

必要なAIモデルを事前にダウンロードできます：

```bash
# モデルダウンローダーを実行
./download_models.sh

# または手動で実行
source venv/bin/activate
python download_models.py
```

ダウンロードオプション：
- **基本モデル（約4GB）**: SD1.5 + All-In-One Pixel Model
- **推奨モデル（約8GB）**: 上記 + スプライトシート生成モデル
- **全モデル（約15GB）**: すべての利用可能なモデル

> 💡 ヒント: 初回起動時に自動的にダウンロードされますが、事前ダウンロードで待ち時間を短縮できます。

### 4. アプリケーション起動

#### Web版（ブラウザー）
```bash
# Web版起動スクリプトを実行（自動で仮想環境作成・依存関係インストール）
./start_server.sh
```

#### デスクトップ版（pygame）
```bash
# デスクトップ版起動スクリプトを実行
./start_pygame.sh
```

初回起動時は、Stable Diffusionモデルのダウンロードが自動で行われます（約4GB、数分かかります）。

### 5. アプリケーション使用

#### Web版
1. ブラウザで http://localhost:5001 にアクセス
2. プロンプトを入力（例：「可愛い猫の戦士」または「a cute cat warrior」）
3. 必要に応じてパラメータを調整
4. 「ピクセルアートを生成」ボタンをクリック
5. 生成された画像をダウンロード

#### デスクトップ版
1. pygame アプリケーションが自動で起動
2. プロンプトを入力
3. スライダーでパラメータを調整
4. 「ピクセルアートを生成」ボタンをクリック（またはCtrl+Enter）
5. 「保存」ボタンで画像を保存（またはCtrl+S）

### 6. アプリケーション停止

```bash
# Web版停止スクリプトを実行
./stop_server.sh

# デスクトップ版: ウィンドウを閉じるか、ターミナルで Ctrl+C
```

## 🎨 使用方法

### 基本的な生成

1. **プロンプト入力**: 日本語または英語で画像の説明を入力
   
   **🇯🇵 日本語プロンプト例:**
   - 「可愛い猫の戦士が森にいる」
   - 「魔法使いが呪文を唱えている」
   - 「勇敢な騎士が剣を持っている」
   - 「青い海の美しい人魚」
   - 「星空を飛ぶ宇宙船」
   
   **🇺🇸 英語プロンプト例:**
   - 「a brave knight with a sword」
   - 「a magical forest with glowing trees」
   - 「a cute dragon sleeping in a cave」

2. **スタイル選択**: プリセットから選択
   - **8-bit**: ファミコン風のドット絵
   - **16-bit**: スーパーファミコン風の細かいドット
   - **ゲームボーイ風**: 緑っぽいモノトーン4色
   - **ミニマル**: シンプルで洗練されたデザイン
   - **高精細**: 細かく美しい表現

3. **パラメータ調整** (詳細設定):
   - **ピクセルサイズ**: 大きいほど粗いピクセル感
   - **カラーパレット**: 使用色数の制限
   - **ステップ数**: 生成品質（多いほど高品質だが時間がかかる）
   - **ガイダンス**: プロンプトへの忠実度

### 🕹️ 4方向スプライトシート生成（NEW!）

ゲーム開発向けに、キャラクターの前後左右4方向のスプライトを自動生成できます。

**使用方法:**
1. キャラクターの説明を入力（例: `warrior character`, `cute cat sprite`）
2. 「4方向スプライトシートを生成」ボタンをクリック
3. 2×2のグリッドで4方向のスプライトが生成されます

**生成される方向:**
- 左上: 前向き（Front）
- 右上: 右向き（Right）
- 左下: 後向き（Back）
- 右下: 左向き（Left）

**推奨設定:**
- サイズ: 512×512px
- ピクセルサイズ: 16
- カラーパレット: 8色

### 🤖 AIモデル選択

Pixaは複数のピクセルアート特化モデルから選択できます：

1. **All-In-One Pixel Model（推奨）🎮**
   - 最も汎用性の高いピクセルアートモデル
   - スタイル: `pixelsprite`（キャラ）、`16bitscene`（背景）
   - 高品質で安定した結果

2. **スプライトシート生成（4方向）🕹️**
   - ゲーム開発向け4方向スプライト自動生成
   - 前後左右の一貫性のあるキャラクタースプライト
   - RPGやアクションゲーム開発に最適

3. **Pixel Art Style（シンプル）🎨**
   - ⚠️ 現在M2 Proで不具合あり（代替モデル推奨）
   - シンプルなピクセルアートスタイル
   - トリガー: `pixelartstyle`

4. **Pixel Art XL LoRA（高速）✨**
   - 高速生成（8ステップ）
   - 高解像度対応
   - トリガー: `pixel`を追加

5. **Stable Diffusion v1.5（標準）**
   - 汎用モデル
   - プロンプトに`pixel art style`を追加して使用

### 🇯🇵 日本語プロンプト機能

Pixaは日本語プロンプトを自動的に英語に翻訳してStable Diffusionに送信します：

**翻訳例:**
- 「可愛い猫の戦士」 → 「cute cat warrior」
- 「魔法の森の城」 → 「magical forest castle」
- 「青い海を飛ぶドラゴン」 → 「blue ocean flying dragon」

**ネガティブプロンプトも日本語対応:**
- 「ぼやけた、低品質」 → 「blurry, low quality」
- 「変な手、余分な指」 → 「weird hands, extra fingers」
- 「暗い、ノイズ」 → 「dark, noise」

### 🎬 アニメーション生成機能

静止画をアニメーション化できる機能を搭載しています。

**動きのタイプ:**
- **ゆらゆら（待機モーション）**: キャラクターの上下動
- **ぴょんぴょん（歩くような動き）**: 左右に傾く歩行動作
- **ジャンプ（弾むような動き）**: バウンス効果
- **キラキラ（光る効果）**: 明るさが変化する発光エフェクト
- **くるくる（回転）**: 360度回転

**使用方法:**
1. 静止画を生成
2. 「アニメーション化」ボタンをクリック
3. 動きのタイプを選択
4. 滑らかさと速さを調整
5. 「アニメーションを生成」ボタンをクリック

## 🔧 技術詳細

### システム要件

- **OS**: macOS 12 (Monterey) 以降
- **チップ**: M2 Pro推奨（M1、Intel Macでも動作）
- **メモリ**: 16GB以上推奨
- **ストレージ**: 15GB以上の空き容量

### アーキテクチャ

```
pixa/
├── backend/              # Python Flask サーバー
│   ├── server.py        # メインサーバーコード
│   ├── model_configs.py # モデル設定
│   └── requirements.txt # Python依存関係
├── frontend/            # Web UI
│   ├── index.html      # メインHTML
│   ├── style.css       # スタイルシート
│   └── app.js          # JavaScript
├── models/              # ダウンロードされたモデル
├── configs/             # 設定ファイル
├── pygame_app*.py       # デスクトップ版アプリ各種
├── download_models.py   # モデルダウンローダー
├── check_available_models.py # モデル確認ツール
├── start_server.sh      # Web版起動スクリプト
├── start_pygame.sh      # デスクトップ版起動スクリプト
├── stop_server.sh       # 停止スクリプト
├── README.md            # このファイル
└── LICENSE              # MIT License
```

### 使用技術

- **バックエンド**: Python, Flask, PyTorch, Diffusers
- **AI モデル**: 
  - Stable Diffusion v1.5
  - PublicPrompts/All-In-One-Pixel-Model
  - Onodofthenorth/SD_PixelArt_SpriteSheet_Generator
  - kohbanye/pixel-art-style
  - nerijs/pixel-art-xl (LoRA)
- **最適化**: Apple MPS (Metal Performance Shaders)
- **Web版**: HTML5, CSS3, JavaScript, Bootstrap 5
- **デスクトップ版**: pygame, pygame-gui

## 🎯 パフォーマンス最適化

### M2 Pro向け最適化

- Metal Performance Shaders (MPS) による GPU加速
- 統合メモリアーキテクチャの効率活用
- Attention slicing によるメモリ使用量削減
- xFormers による高速化（利用可能な場合）

### 生成時間の目安

- **512×512px, 20steps**: 約10-15秒 (M2 Pro)
- **256×256px, 20steps**: 約5-8秒 (M2 Pro)
- **768×768px, 30steps**: 約20-30秒 (M2 Pro)
- **4方向スプライトシート**: 約40-60秒 (M2 Pro)
- **アニメーション 512×512px, 8フレーム**: 約40-60秒 (M2 Pro)

## 🔍 トラブルシューティング

### よくある問題

1. **「サーバーに接続できません」エラー**
   - バックエンドサーバーが起動しているか確認
   - ポート5001が他のアプリケーションで使用されていないか確認

2. **pixel-art-styleモデルが真っ黒な画像を生成する**
   - 既知の問題です。代わりにAll-In-One Pixel Modelを使用してください
   - または、SD1.5に`pixel art style`を追加して使用

3. **生成が非常に遅い**
   - MPSが有効になっているか確認: `python -c "import torch; print(torch.backends.mps.is_available())"`
   - メモリ不足の可能性：他のアプリケーションを閉じてみる

4. **メモリエラー**
   - 画像サイズを小さくする（512px → 256px）
   - ステップ数を減らす（30 → 20）

### モデル確認ツール

```bash
# ダウンロード済みモデルを確認
python check_available_models.py
```

## 📝 プロンプトのコツ

### 効果的なプロンプト作成

1. **モデル別のトリガーワード**:
   - All-In-One: `pixelsprite` または `16bitscene`
   - Pixel Art XL: プロンプトに `pixel` を追加
   - Pixel Art Style: `pixelartstyle` を先頭に

2. **具体的に記述**:
   - ❌ `a character`
   - ✅ `pixelsprite, a brave medieval knight with blue armor`

3. **品質向上キーワード**:
   - `high quality`, `detailed`, `clean lines`, `game asset`

4. **ネガティブプロンプトの活用**:
   - `blurry, low quality, 3d render, realistic, smooth shading`

### プロンプト例

```
# All-In-One Pixel Model
pixelsprite, cute cat warrior, simple design, game character
16bitscene, magical forest background, vibrant colors

# スプライトシート用
warrior character, clean sprite design, simple colors
cute robot, game asset, clear silhouette

# 一般的なピクセルアート
pixel art style, 8-bit, retro game sprite, a wizard casting spells
```

## 🤝 サポート

### 開発環境

```bash
# 開発モードでサーバーを起動（デバッグ有効）
cd backend
python server.py --debug

# モデル設定の確認
python -c "from model_configs import MODEL_CONFIGS; print(MODEL_CONFIGS.keys())"
```

### ユーティリティスクリプト

- `check_available_models.py`: ダウンロード済みモデルの確認
- `download_models.py`: モデルの個別ダウンロード
- `enable_pixel_art_style.py`: pixel-art-styleモデルの設定

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご確認ください。

## 🔄 更新履歴

### 2025年5月24日（最新）
- 4方向スプライトシート生成機能を追加
- スプライトシート生成ボタンを常時表示に変更
- pixel-art-styleモデルのVAEサポートとフォールバック機能を追加
- 複数のユーティリティスクリプトを追加
- モデル管理機能を強化
- ドキュメントの大幅な更新

### 2025年5月23日
- 複数のピクセルアート特化モデルを追加
- モデル自動ダウンロード機能を実装
- アニメーション生成のワークフローを改善
- 日本語対応を強化

## 🙏 謝辞

- [Stability AI](https://stability.ai/) - Stable Diffusion
- [Hugging Face](https://huggingface.co/) - Diffusers ライブラリ
- [PublicPrompts](https://huggingface.co/PublicPrompts) - All-In-One-Pixel-Model
- [Onodofthenorth](https://huggingface.co/Onodofthenorth) - SD_PixelArt_SpriteSheet_Generator
- [Apple](https://developer.apple.com/) - Metal Performance Shaders