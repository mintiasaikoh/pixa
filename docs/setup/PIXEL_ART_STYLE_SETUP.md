# pixel-art-styleモデルの使い方

## ダウンロード方法

pixel-art-styleモデルは4.1GBの`.ckpt`ファイルを使用します。

```bash
# 1. 仮想環境をアクティベート
cd /Users/mymac/pixa
source venv/bin/activate

# 2. モデルをダウンロード
huggingface-cli download kohbanye/pixel-art-style pixel-art-style.ckpt --local-dir ./models/pixel-art-style
```

## 使用方法

1. 上記コマンドでモデルをダウンロード
2. サーバーを再起動（`./stop_server.sh` → `./start_server.sh`）
3. UIで「Pixel Art Style（シンプル）🎨」を選択
4. プロンプトに自動的に`pixelartstyle`が追加されます
5. 生成！

## 特徴

- シンプルで綺麗なピクセルアート
- トリガーワード: `pixelartstyle`
- 推奨設定:
  - ピクセルサイズ: 8
  - パレット: 16色
  - ステップ数: 20
  - ガイダンス: 7.5

## トラブルシューティング

もしエラーが出た場合:
- ファイルが正しい場所にあるか確認: `ls -la ./models/pixel-art-style/`
- ファイルサイズが4.1GBあるか確認
- サーバーログを確認: `tail -f server.log`
