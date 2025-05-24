# 📁 Scripts Directory

このディレクトリには、Pixaプロジェクトの各種スクリプトが整理されています。

## 📂 ディレクトリ構成

### 🔧 utils/ - ユーティリティスクリプト
モデル管理やダウンロード関連のスクリプト

- `check_available_models.py` - ダウンロード済みモデルの確認
- `download_models.py` - インタラクティブなモデルダウンローダー
- `download_essential_models.py` - 必須モデルの自動ダウンロード
- `download_sd15_only.py` - SD1.5のみダウンロード
- `enable_pixel_art_style.py` - pixel-art-styleモデルの設定
- `download_all_basic.sh` - 基本モデル一括ダウンロード
- `download_missing_only.sh` - 不足モデルのみダウンロード
- `quick_download.sh` - クイックダウンロード

### 🧪 tests/ - テストスクリプト
動作確認やサンプル生成用のスクリプト

- `test_animation.py` - アニメーション機能のテスト
- `test_pixel_art_style.py` - pixel-art-styleモデルのテスト
- `generate_cat_computer.py` - サンプル画像生成（猫とコンピュータ）
- `generate_cat_computer_gif.py` - サンプルGIF生成

### 🛠️ tools/ - 開発ツール
最適化やビルド関連のツール

- `analyze_optimization.py` - 最適化可能項目の分析
- `apply_optimizations.py` - 最適化パッチの適用
- `measure_performance.py` - パフォーマンス測定
- `optimization_report.py` - 最適化レポート生成
- `optimization_patch.py` - 最適化パッチコード
- `build_dmg.sh` - macOS DMGパッケージビルド

## 🚀 使い方

```bash
# ユーティリティの実行例
python scripts/utils/check_available_models.py

# テストの実行例
python scripts/tests/test_animation.py

# ツールの実行例
python scripts/tools/optimization_report.py
```
