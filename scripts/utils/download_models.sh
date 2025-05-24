#!/bin/bash

# Pixaモデルダウンロードスクリプト

echo "🎨 Pixa - モデルダウンローダー"
echo ""

# venvのアクティベート
if [ -f "venv/bin/activate" ]; then
    echo "📦 仮想環境を有効化しています..."
    source venv/bin/activate
else
    echo "❌ エラー: 仮想環境が見つかりません"
    echo "   先に ./start_server.sh を実行してセットアップしてください"
    exit 1
fi

# huggingface_hubがインストールされているか確認
if ! python -c "import huggingface_hub" 2>/dev/null; then
    echo "📥 huggingface_hub をインストールしています..."
    pip install huggingface-hub
fi

# ダウンロードスクリプトを実行
python download_models.py
