# 🎯 Project Structure

ルートディレクトリをクリーンに保つため、スクリプトを以下のように整理しました：

## 📁 主要ディレクトリ

- **backend/** - Flaskサーバー（AIモデル処理）
- **frontend/** - Web UI（HTML/CSS/JavaScript）
- **apps/** - デスクトップ版アプリ（pygame）
- **scripts/** - 各種ユーティリティスクリプト
  - **utils/** - モデル管理、ダウンロード
  - **tests/** - テスト、サンプル生成
  - **tools/** - 開発ツール、最適化
- **models/** - ダウンロードされたAIモデル
- **configs/** - 設定ファイル

## 🚀 クイックスタート

```bash
# Web版を起動
./start_server.sh

# デスクトップ版を起動
./start_pygame.sh

# サーバーを停止
./stop_server.sh
```

詳細は[README.md](README.md)をご覧ください。
