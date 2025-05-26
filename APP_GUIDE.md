# 🚀 Pixa.app作成ガイド

Pixaをダブルクリックで起動できるmacOSアプリケーション（.app）を作成する方法です。

## 📱 利用可能な.appタイプ

### 1. **Pixa.app** - シンプル版
最も簡単な方法。ターミナルを開いてサーバーを起動します。

```bash
# 作成方法
chmod +x create_app.sh
./create_app.sh

# 使い方
ダブルクリックで起動
```

**特徴:**
- ✅ シンプルで分かりやすい
- ✅ ターミナルウィンドウが表示される
- ✅ ログがリアルタイムで見える
- ❌ ターミナルを閉じるとサーバーも停止

### 2. **Pixa Pro.app** - プロフェッショナル版
バックグラウンドでサーバーを起動する高度な版。

```bash
# 作成方法
chmod +x create_app_pro.sh
./create_app_pro.sh

# 使い方
ダブルクリックで起動
./stop_pixa.sh で停止
```

**特徴:**
- ✅ バックグラウンドで動作
- ✅ ログファイルに記録（~/Library/Logs/Pixa/）
- ✅ 自動的に依存関係をインストール
- ✅ プロフェッショナルな動作
- ❌ 設定がやや複雑

### 3. **Pixa Desktop.app** - Pygame版
デスクトップアプリケーション版（pygame）を起動。

```bash
# 作成方法
chmod +x create_app_desktop.sh
./create_app_desktop.sh

# 使い方
ダブルクリックで起動
```

**特徴:**
- ✅ ネイティブデスクトップアプリ
- ✅ ブラウザ不要
- ✅ 高速な応答
- ❌ Web版とは異なるUI

## 🛠️ セットアップ手順

### 基本的な手順

1. **スクリプトに実行権限を付与**
   ```bash
   chmod +x create_app.sh
   chmod +x create_app_pro.sh
   chmod +x create_app_desktop.sh
   ```

2. **お好みの.appを作成**
   ```bash
   # シンプル版
   ./create_app.sh

   # プロ版
   ./create_app_pro.sh

   # デスクトップ版
   ./create_app_desktop.sh
   ```

3. **Applicationsフォルダに移動（オプション）**
   ```bash
   # シンプル版
   mv Pixa.app /Applications/

   # プロ版
   mv "Pixa Pro.app" /Applications/

   # デスクトップ版
   mv "Pixa Desktop.app" /Applications/
   ```

## 🔒 セキュリティ設定

初回起動時にmacOSのセキュリティ警告が表示される場合があります。

### 対処方法:
1. **システム環境設定** → **セキュリティとプライバシー**
2. 「一般」タブで「このまま開く」をクリック
3. または、右クリック → 「開く」で起動

## 📁 ファイル構成

```
pixa/
├── create_app.sh          # シンプル版作成スクリプト
├── create_app_pro.sh      # プロ版作成スクリプト
├── create_app_desktop.sh  # デスクトップ版作成スクリプト
├── Pixa.app/             # 生成されたアプリ（シンプル版）
├── Pixa Pro.app/         # 生成されたアプリ（プロ版）
├── Pixa Desktop.app/     # 生成されたアプリ（デスクトップ版）
└── stop_pixa.sh          # サーバー停止スクリプト（プロ版用）
```

## 🎨 カスタマイズ

### アイコンの変更
1. `AppIcon.icns`ファイルを用意
2. スクリプト実行前に同じディレクトリに配置
3. 自動的にアプリに組み込まれます

### パスの変更
スクリプト内の`pixaPath`を実際のパスに変更:
```applescript
set pixaPath to "/Users/あなたのユーザー名/pixa"
```

## 🚦 トラブルシューティング

### アプリが起動しない
- Pixaプロジェクトのパスが正しいか確認
- Python 3がインストールされているか確認
- ターミナルで`./start_server.sh`が動作するか確認

### ポート5001が使用中
- 既存のPixaサーバーが動作していないか確認
- `./stop_pixa.sh`でサーバーを停止

### ログの確認（プロ版）
```bash
# ログファイルを表示
tail -f ~/Library/Logs/Pixa/pixa.log
```

## 💡 おすすめの使い方

- **開発中**: シンプル版（ログが見やすい）
- **日常使用**: プロ版（バックグラウンド動作）
- **オフライン作業**: デスクトップ版（高速）

## 📝 注意事項

- .appファイルは`git`に含めないでください（.gitignoreに追加済み）
- アプリ作成後も元のシェルスクリプトは使用可能です
- 複数のバージョンを同時にインストール可能

---

**作成日**: 2025年5月26日
**バージョン**: 1.0.0