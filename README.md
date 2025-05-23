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
- **🇯🇵 ネガティブプロンプト日本語対応**: 避けたい要素も日本語で指定可能
- **🤖 AIモデル切り替え**: 複数のStable Diffusionモデルから選択可能
- **📊 詳細パラメーター説明**: 各設定項目にわかりやすい説明文を表示

## 🚀 クイックスタート

### 1. 事前準備

以下がインストールされていることを確認してください：

- Python 3.8以上
- pip (Python package manager)
- 十分な空き容量（モデルファイル用に約5GB）

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

### 3. アプリケーション起動

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

初回起動時は、Stable Diffusionモデルのダウンロードが自動で行われます（約5GB、数分かかります）。

### 4. アプリケーション使用

#### Web版
1. ブラウザで http://localhost:5001 にアクセス
2. プロンプトを入力（例：「可愛い猫の戦士」または「a cute cat warrior in a forest」）
3. 必要に応じてパラメータを調整
4. 「ピクセルアートを生成」ボタンをクリック
5. 生成された画像をダウンロード

#### デスクトップ版
1. pygame アプリケーションが自動で起動
2. プロンプトを入力
3. スライダーでパラメータを調整
4. 「ピクセルアートを生成」ボタンをクリック（またはCtrl+Enter）
5. 「保存」ボタンで画像を保存（またはCtrl+S）

### 5. アプリケーション停止

```bash
# Web版停止スクリプトを実行
./stop_server.sh

# デスクトップ版: ウィンドウを閉じるか、ターミナルで Ctrl+C

# または起動中のターミナルで Ctrl+C
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

**対応語彙:**
- 動物: 猫、犬、ドラゴン、馬、うさぎ等
- キャラクター: 騎士、魔法使い、忍者、侍等
- 場所: 城、森、海、山、空等
- 形容詞: 可愛い、美しい、強い、魔法の等
- ネガティブ用語: ぼやけた、低品質、変な、歪んだ、崩れた、汚い、醜い等
- アニメーション: 歩く、走る、ジャンプ、待機、アイドル、回転、光る等

### 高度な機能

- **ネガティブプロンプト**: 避けたい要素を指定（日本語対応）
  - 例: 「ぼやけた、低品質、変な手」
- **シード値**: 同じ結果を再現するための値
- **画像サイズ**: 256px〜768pxまで選択可能
- **クイックプロンプト**: よく使用されるプロンプトのワンクリック入力

### 🎬 アニメーション生成機能

Pixaは静止画をアニメーション化できる機能を搭載しています。

**新しいワークフロー:**
1. まず通常通り静止画を生成
2. 気に入った画像の「アニメーション化」ボタンをクリック
3. アニメーション設定を調整
4. 何度でも設定を変えてアニメーション生成可能
5. 新しい静止画が欲しい場合は「新しい静止画を生成する」ボタン

**動きのタイプ:**
- **ゆらゆら（待機モーション）**: キャラクターの上下動
- **ぴょんぴょん（歩くような動き）**: 左右に傾く歩行動作
- **ジャンプ（弾むような動き）**: バウンス効果
- **キラキラ（光る効果）**: 明るさが変化する発光エフェクト
- **くるくる（回転）**: 360度回転

**アニメーションパラメータ:**
- **動きの滑らかさ**: 2〜16コマ（フレーム数）
- **動きの速さ**: 5（ゆっくり）〜30（速い）

**使用方法:**
1. 静止画を生成
2. 「アニメーション化」ボタンをクリック
3. 動きのタイプを選択
4. 滑らかさと速さを調整
5. 「アニメーションを生成」ボタンをクリック
6. 生成されたGIFは「GIFダウンロード」ボタンで保存可能

### 🤖 AIモデル切り替え機能

Pixaは複数のStable Diffusionモデルから選択して生成できます。モデルごとに異なる特徴があり、用途に応じて使い分けることができます。

**利用可能なモデル:**

1. **Stable Diffusion v1.5（標準）**
   - 汎用的な画像生成モデル
   - バランスの取れた生成品質
   - ピクセルアート以外も生成可能

2. **Anything v3.0（アニメ調）**
   - アニメ・マンガ風のキャラクター生成に特化
   - 日本のゲーム風のビジュアル
   - かわいいキャラクター生成に最適

3. **Pixel Art XL（高解像度）**  
   - 高解像度（1024×1024）のピクセルアート生成
   - より詳細で現代的なピクセルアート
   - 8GB以上のVRAM推奨

**モデル切り替え方法:**
1. UIの「AIモデル」ドロップダウンから選択
2. 選択すると自動的に推奨設定が適用される
3. 初回選択時はモデルのダウンロードが行われる（数GB）

**モデル別推奨設定（自動適用）:**
- **Anything v3.0**: ピクセルサイズ6、色数24
- **Pixel Art XL**: ピクセルサイズ4、色数32、画像サイズ1024×1024

### 📊 詳細パラメーターの説明

UIの詳細パラメーターセクションには、各設定項目にわかりやすい説明文が表示されるようになりました：

- **ピクセルサイズ**: ドットの大きさ（大きいほど粗いピクセルアート）
- **カラーパレット**: 使用する色数（少ないほどレトロな雰囲気）
- **ステップ数**: 生成の詳細度（多いほど高品質だが時間がかかる）
- **ガイダンス**: プロンプトへの忠実度（高いほどプロンプトに従う）

## 🔧 技術詳細

### システム要件

- **OS**: macOS 12 (Monterey) 以降
- **チップ**: M2 Pro推奨（M1、Intel Macでも動作）
- **メモリ**: 16GB以上推奨
- **ストレージ**: 10GB以上の空き容量

### アーキテクチャ

```
pixa/
├── backend/           # Python Flask サーバー
│   ├── server.py     # メインサーバーコード
│   └── requirements.txt  # Python依存関係
├── frontend/         # Web UI
│   ├── index.html    # メインHTML
│   ├── style.css     # スタイルシート
│   └── app.js        # JavaScript
├── pygame_app.py     # デスクトップ版 pygame アプリ
├── start_server.sh   # Web版起動スクリプト
├── start_pygame.sh   # デスクトップ版起動スクリプト
├── stop_server.sh    # 停止スクリプト
├── README.md         # このファイル
└── LICENSE           # MIT License
```

### 依存関係 (requirements.txt)

```
flask==2.3.2
flask-cors==4.0.0
torch>=2.0.0
diffusers>=0.21.0
transformers>=4.30.0
accelerate>=0.20.0
safetensors>=0.3.1
Pillow>=9.5.0
numpy>=1.24.0
imageio>=2.31.0
pygame
pygame-gui
requests
```

### 使用技術

- **バックエンド**: Python, Flask, PyTorch, Diffusers
- **AI モデル**: 
  - Stable Diffusion v1.5（標準）
  - Anything v3.0（アニメ調）
  - Pixel Art XL（高解像度）
- **最適化**: Apple MPS (Metal Performance Shaders)
- **Web版**: HTML5, CSS3, JavaScript, Bootstrap 5
- **デスクトップ版**: pygame, pygame-gui

## 🎯 パフォーマンス最適化

### M2 Pro向け最適化

- Metal Performance Shaders (MPS) による GPU加速
- 統合メモリアーキテクチャの効率活用
- Attention slicing によるメモリ使用量削減
- xFormers による高速化

### 生成時間の目安

- **512×512px, 20steps**: 約10-15秒 (M2 Pro)
- **256×256px, 20steps**: 約5-8秒 (M2 Pro)
- **768×768px, 30steps**: 約20-30秒 (M2 Pro)
- **アニメーション 512×512px, 4フレーム**: 約20-30秒 (M2 Pro)
- **アニメーション 512×512px, 8フレーム**: 約40-60秒 (M2 Pro)

## 🔍 トラブルシューティング

### よくある問題

1. **「サーバーに接続できません」エラー**
   - バックエンドサーバーが起動しているか確認
   - ポート5000が他のアプリケーションで使用されていないか確認

2. **生成が非常に遅い**
   - MPSが有効になっているか確認: `python -c "import torch; print(torch.backends.mps.is_available())"`
   - メモリ不足の可能性：他のアプリケーションを閉じてみる

3. **メモリエラー**
   - 画像サイズを小さくする（512px → 256px）
   - ステップ数を減らす（30 → 20）

4. **「Pipeline not initialized」エラー**
   - サーバーログを確認してモデルのダウンロード状況をチェック
   - 十分な空き容量があることを確認

### ログの確認

```bash
# サーバーのログを確認
tail -f logs/server.log

# Python環境の確認
python -c "
import torch
from diffusers import StableDiffusionPipeline
print('✅ すべてのライブラリが正常にインストールされています')
"
```

## 📝 プロンプトのコツ

### 効果的なプロンプト作成

1. **具体的に記述**:
   - ❌ `a character`
   - ✅ `a brave medieval knight with blue armor`

2. **スタイルキーワードを追加**:
   - `pixel art`, `8-bit style`, `retro game`, `sprite`

3. **品質向上キーワード**:
   - `high quality`, `detailed`, `clean lines`

4. **ネガティブプロンプトの活用**:
   - 英語: `blurry, low quality, bad anatomy, deformed`
   - 日本語: `ぼやけた、低品質、変な手、歪んだ`

### プロンプト例

```
# キャラクター
a cute cat wizard casting spells, pixel art style, 8-bit, magical forest background

# 風景
a mystical castle on a floating island, pixel art, retro game style, clouds and stars

# オブジェクト
a magical sword with glowing runes, pixel art sprite, 16-bit style, transparent background

# アニメーション用
a pixel art knight character, side view, clean sprite sheet style
a cute slime monster, simple design, suitable for animation
a flying dragon, pixel art, clear silhouette
```

## 🤝 サポート

### 開発環境

```bash
# 開発モードでサーバーを起動（デバッグ有効）
cd backend
python server.py --debug

# フロントエンドの開発サーバー
cd frontend
python -m http.server 8080
```

### 貢献

このプロジェクトは要件定義書に基づいて開発されています。改善提案や新機能のアイデアがある場合は、GitHubのIssuesをご利用ください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご確認ください。

## 🔄 更新履歴

### 2025年5月23日（最新）
- AIモデル切り替え機能を追加（Stable Diffusion v1.5、Anything v3.0、Pixel Art XL）
- モデル選択時に推奨設定を自動適用する機能を実装
- 詳細パラメーターに説明文を追加（ピクセルサイズ、カラーパレット、ステップ数、ガイダンス）
- UIの色設定を改善（統一感のある白文字表示）
- モデル選択UIのデザインを強調表示

### 2025年5月23日（初期版）
- NFT関連機能を削除
- スタイルプリセットを改善（8-bit、16-bit、ゲームボーイ風、ミニマル、高精細）
- ネガティブプロンプトの日本語対応を追加
- アニメーション生成のワークフローを改善（静止画→アニメーション化）
- アニメーション設定UIを日本語化（動きのタイプ、滑らかさ、速さ）

## 🙏 謝辞

- [Stability AI](https://stability.ai/) - Stable Diffusion
- [Hugging Face](https://huggingface.co/) - Diffusers ライブラリ
- [Apple](https://developer.apple.com/) - Metal Performance Shaders