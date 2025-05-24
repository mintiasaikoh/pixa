#!/bin/bash

# Pixa pygame版 起動スクリプト

echo "=== Pixa pygame版 起動 ==="

# 仮想環境の確認・作成
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係インストール
echo "依存関係をインストール中..."
pip install -r backend/requirements.txt

# バックエンドサーバー起動（バックグラウンド）
echo "バックエンドサーバーを起動中..."
cd backend
python server.py &
SERVER_PID=$!
cd ..

# サーバー起動を少し待つ
echo "サーバー起動を待機中..."
sleep 5

# pygame アプリケーション起動
echo "pygame アプリケーションを起動中..."
python apps/pygame_app_improved.py

# 終了時にサーバーを停止
echo "アプリケーション終了。サーバーを停止中..."
kill $SERVER_PID 2>/dev/null

echo "=== 終了 ==="