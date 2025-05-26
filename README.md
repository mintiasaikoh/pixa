# 🎨 Pixa - AI ピクセルアート ジェネレーター

レトロゲーム風のピクセルアートを簡単に生成できるAIアプリケーション（M2 Pro Mac最適化版）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-M1%2FM2-orange.svg)](https://support.apple.com/en-us/HT211814)

## ✨ 主な特徴

### 🎮 レトロゲーム風テンプレート
ワンクリックでレトロゲーム機風のスタイルを適用：
- **ファミコン風** - 8ビット、シンプルな色使い
- **スーファミ風** - 16ビット、鮮やかな色彩
- **ゲームボーイ風** - モノクロ4階調、緑がかった画面
- **アーケード風** - ネオンカラー、レトロフューチャー

### 📦 統合設定パネル
すべての設定を左パネルに集約：
- **基本設定** - プロンプト入力とモデル選択
- **スタイル設定** - ピクセルサイズ、カラー数、アウトライン
- **生成品質** - 高速/標準/高品質のプリセット
- **その他オプション** - ネガティブプロンプト、アスペクト比

### 🚀 その他の機能
- **日本語対応** - 日本語プロンプトを自動翻訳
- **グリッチアート生成** - AIなしで高速生成
- **アニメーション作成** - 静止画をGIFアニメに
- **Apple Silicon最適化** - M1/M2 Macで高速動作

## 🔧 インストール

### 1. リポジトリをクローン
```bash
git clone https://github.com/mintiasaikoh/pixa.git
cd pixa
```

### 2. 起動（自動セットアップ）
```bash
./start_server.sh
```

初回起動時は以下が自動的に行われます：
- Python仮想環境の作成
- 必要なパッケージのインストール
- AIモデルのダウンロード（約4GB）

### 3. ブラウザでアクセス
http://localhost:5001 が自動的に開きます

## 🎨 使い方

### 基本的な流れ

1. **レトロゲーム風スタイルを選択**
   - 「🎮 ファミコン風」などのボタンをクリック

2. **プロンプトを編集**（オプション）
   - 例：「ファミコン風8ビットピクセルアート、勇者キャラクター」

3. **生成品質を選択**
   - ⚡ 高速（プレビュー用）
   - ⚖️ 標準（バランス重視）
   - 💎 高品質（最高品質）

4. **生成ボタンをクリック**
   - 10-15秒で画像が生成されます

### 詳細設定（アコーディオンを開いて調整）

**スタイル設定**
- ピクセルサイズ：2-16px（大きいほど粗いドット）
- カラーパレット：2-64色（少ないほどレトロ）
- アウトライン：ON/OFF

**生成品質**
- ステップ数：10-50（多いほど高品質）
- プロンプト強度：1-20（高いほど忠実）
- シード値：-1でランダム

**その他オプション**
- ネガティブプロンプト：除外したい要素
- アスペクト比：1:1、16:9、9:16、4:3

## 📚 ドキュメント

詳細は[docs](./docs/)フォルダを参照：
- 📖 [ドキュメント一覧](./docs/README.md)
- 🔧 [セットアップガイド](./docs/setup/)
- ✨ [機能説明](./docs/features/)
- 🎨 [UI関連](./docs/ui/)

## 🖥️ システム要件

- **OS**: macOS 12 (Monterey) 以降
- **CPU**: Apple Silicon (M1/M2) または Intel Mac
- **メモリ**: 8GB以上（16GB推奨）
- **ストレージ**: 10GB以上の空き容量

## 🚀 パフォーマンス

M2 Pro Macでの生成時間目安：
- 512×512px, 標準品質: 約10-15秒
- 512×512px, 高速: 約5-8秒
- 512×512px, 高品質: 約20-30秒

## 🔧 トラブルシューティング

### サーバーが起動しない
```bash
# Pythonバージョンを確認
python3 --version  # 3.8以上が必要

# 手動で仮想環境を作成
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 生成が遅い
- Apple Siliconの場合、MPSが有効か確認
- メモリ不足の場合は他のアプリを終了

### エラーが出る
```bash
# ログを確認
tail -f server.log
```

## 📝 更新履歴

### 2025年5月27日（最新）
- 🎮 レトロゲーム風テンプレート実装
- 📦 統合設定パネル（アコーディオン式）
- ⚡ 品質プリセット機能
- 🧹 リポジトリ整理

詳細な変更履歴は[こちら](./docs/changelog/)

## 📄 ライセンス

MITライセンス - 詳細は[LICENSE](LICENSE)を参照

## 🙏 謝辞

- [Stability AI](https://stability.ai/) - Stable Diffusion
- [Hugging Face](https://huggingface.co/) - Diffusers ライブラリ
- [PublicPrompts](https://huggingface.co/PublicPrompts) - All-In-One-Pixel-Model