# 🎨 AI ピクセルアート ジェネレーター

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
- **⚡ 高速生成**: 512×512px画像が約10-15秒
- **🇯🇵 日本語プロンプト対応**: 「可愛い猫の戦士」などの日本語入力対応
- **🎯 複数のスタイルプリセット**: 8-bit、16-bit、RPG、アーケードスタイル

## 🚀 クイックスタート

### 1. 事前準備

以下がインストールされていることを確認してください：

- Python 3.8以上
- pip (Python package manager)
- 十分な空き容量（モデルファイル用に約5GB）

### 2. アプリケーション起動

```bash
# プロジェクトディレクトリに移動
cd /Users/mymac/fracta/ai-pixel-generator

# 起動スクリプトを実行
./start_server.sh
```

初回起動時は、依存関係のインストールとStable Diffusionモデルのダウンロードが自動で行われます。

### 3. アプリケーション使用

1. ブラウザで http://localhost:8080 にアクセス
2. プロンプトを入力（例：「a cute cat warrior in a forest」）
3. 必要に応じてパラメータを調整
4. 「ピクセルアートを生成」ボタンをクリック
5. 生成された画像をダウンロード

### 4. アプリケーション停止

```bash
# 停止スクリプトを実行
./stop_server.sh

# または起動中のターミナルで Ctrl+C
```

## 🎨 使用方法

### 基本的な生成

1. **プロンプト入力**: 生成したい画像の説明を英語で入力
   - 例：「a brave knight with a sword」
   - 例：「a magical forest with glowing trees」

2. **スタイル選択**: プリセットから選択
   - **8-bit クラシック**: レトロゲーム風
   - **16-bit ゲーム**: より詳細なピクセルアート
   - **RPG スプライト**: RPGキャラクター風
   - **アーケードスタイル**: アーケードゲーム風

3. **パラメータ調整** (詳細設定):
   - **ピクセルサイズ**: 大きいほど粗いピクセル感
   - **カラーパレット**: 使用色数の制限
   - **ステップ数**: 生成品質（多いほど高品質だが時間がかかる）
   - **ガイダンス**: プロンプトへの忠実度

### 高度な機能

- **ネガティブプロンプト**: 避けたい要素を指定
- **シード値**: 同じ結果を再現するための値
- **画像サイズ**: 256px〜768pxまで選択可能
- **クイックプロンプト**: よく使用されるプロンプトのワンクリック入力

## 🔧 技術詳細

### システム要件

- **OS**: macOS 12 (Monterey) 以降
- **チップ**: M2 Pro推奨（M1、Intel Macでも動作）
- **メモリ**: 16GB以上推奨
- **ストレージ**: 10GB以上の空き容量

### アーキテクチャ

```
ai-pixel-generator/
├── backend/           # Python Flask サーバー
│   ├── server.py     # メインサーバーコード
│   └── requirements.txt
├── frontend/         # Web UI
│   ├── index.html    # メインHTML
│   ├── style.css     # スタイルシート
│   └── app.js        # JavaScript
├── start_server.sh   # 起動スクリプト
└── stop_server.sh    # 停止スクリプト
```

### 使用技術

- **バックエンド**: Python, Flask, PyTorch, Diffusers
- **AI**: Stable Diffusion v1.5
- **最適化**: Apple MPS (Metal Performance Shaders)
- **フロントエンド**: HTML5, CSS3, JavaScript, Bootstrap 5

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
   - `blurry, low quality, bad anatomy, deformed`

### プロンプト例

```
# キャラクター
a cute cat wizard casting spells, pixel art style, 8-bit, magical forest background

# 風景
a mystical castle on a floating island, pixel art, retro game style, clouds and stars

# オブジェクト
a magical sword with glowing runes, pixel art sprite, 16-bit style, transparent background
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

## 🙏 謝辞

- [Stability AI](https://stability.ai/) - Stable Diffusion
- [Hugging Face](https://huggingface.co/) - Diffusers ライブラリ
- [Apple](https://developer.apple.com/) - Metal Performance Shaders