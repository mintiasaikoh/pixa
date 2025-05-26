# 📚 Pixa ドキュメント

Pixa - AI ピクセルアート ジェネレーターの全ドキュメントです。

## 📁 ドキュメント構成

### 🔧 [セットアップ](./setup/)
- [モデルダウンロードガイド](./setup/DOWNLOAD_MODELS.md) - モデルのダウンロード方法
- [ピクセルアートモデル一覧](./setup/PIXEL_ART_MODELS.md) - 利用可能なモデルの詳細
- [pixel-art-styleセットアップ](./setup/PIXEL_ART_STYLE_SETUP.md) - 特定モデルの設定方法
- [SDXL対応ガイド](./setup/SDXL_GUIDE.md) - SDXL系モデルの利用方法

### ✨ [機能説明](./features/)
- [クリエイティブアニメーション](./features/CREATIVE_ANIMATIONS.md) - アニメーション生成機能
- [レトロゲーム風テンプレート](./features/RETRO_GAME_TEMPLATES.md) - ファミコン/スーファミ風スタイル

### 🎨 [UI関連](./ui/)
- [UI統合完了](./ui/UI_INTEGRATION_COMPLETE.md) - 統合UI実装の詳細
- [UI修正完了](./ui/UI_FIX_COMPLETE.md) - アコーディオン機能等の修正
- [UIレイアウト修正](./ui/UI_LAYOUT_FIX.md) - レイアウトの改善

### 📝 [変更履歴](./changelog/)
- [クリーンアップ完了](./changelog/CLEANUP_COMPLETE.md) - リポジトリ整理の記録
- [レトロテンプレート完了](./changelog/RETRO_COMPLETE.md) - レトロゲーム風実装

### 📋 その他
- [プロジェクト構造](./PROJECT_STRUCTURE.md) - ファイル構成の説明
- [技術詳細](./TECHNICAL_DETAILS.md) - アーキテクチャとAPI仕様
- [README更新履歴](./README_UPDATE.md) - README.mdの変更内容
- [ドキュメント整理](./DOCUMENT_ORGANIZATION.md) - ドキュメント構成

## 🚀 クイックスタート

1. **インストール**
   ```bash
   git clone https://github.com/mintiasaikoh/pixa.git
   cd pixa
   ```

2. **セットアップ**
   ```bash
   ./start_server.sh
   ```

3. **アクセス**
   - ブラウザで http://localhost:5001 を開く

## 🎮 主な機能

### レトロゲーム風テンプレート
- 🎮 ファミコン風（8ビット）
- 🌟 スーファミ風（16ビット）
- 🟩 ゲームボーイ風（モノクロ4階調）
- 🕹️ アーケード風（ネオンカラー）

### 統合設定パネル
- アコーディオン式で整理された設定
- 品質プリセット（高速/標準/高品質）
- 直感的なスライダーとトグル

### アニメーション生成
- ゆらゆら、歩く、弾む、グリッチ波など
- フレーム数とFPSの調整可能

## 📖 詳細ドキュメント

各機能の詳細については、上記のリンクから個別のドキュメントを参照してください。

## 🆘 トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. Python 3.8以上がインストールされているか
2. 必要な依存関係がインストールされているか
3. Apple Silicon Macの場合、MPSが有効になっているか

詳細は各セットアップドキュメントを参照してください。