#!/bin/bash

# Pixa - AI ピクセルアート ジェネレーター サーバー起動スクリプト
# M2 Pro Mac最適化版

echo "🎨 Pixa - AI ピクセルアート ジェネレーター を起動中..."

# 現在のディレクトリを保存
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Python仮想環境の確認と作成
if [ ! -d "venv" ]; then
    echo "📦 Python仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "🔧 仮想環境をアクティベート中..."
source venv/bin/activate

# 必要なパッケージをインストール
echo "📚 依存関係をインストール中..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Apple Silicon (M2 Pro) 最適化の確認
echo "🍎 Apple Silicon最適化の確認中..."
python3 -c "
import torch
print(f'PyTorch バージョン: {torch.__version__}')
print(f'MPS 利用可能: {torch.backends.mps.is_available()}')
print(f'MPS 組み込み済み: {torch.backends.mps.is_built()}')
if torch.backends.mps.is_available():
    print('✅ Apple Silicon (MPS) 最適化が有効です')
else:
    print('⚠️  MPS が利用できません。CPUモードで動作します。')
"

# 統合サーバーを起動
echo "🚀 Pixa統合サーバーを起動中..."
echo "サーバーURL: http://localhost:5001"
echo ""
echo "サーバーを停止するには Ctrl+C を押してください"
echo ""

# 統合サーバーを起動
cd backend
python server.py &
SERVER_PID=$!

# プロセスIDを保存
echo $SERVER_PID > ../server.pid

echo ""
echo "✅ 統合サーバーが起動しました！"
echo "🌐 ブラウザで http://localhost:5001 にアクセスしてください"
echo ""

# ブラウザを自動で開く（オプション）
if command -v open &> /dev/null; then
    echo "🚀 ブラウザを自動で開いています..."
    sleep 5
    open http://localhost:5001
fi

# 終了シグナルをキャッチ
trap 'echo ""; echo "🛑 サーバーを停止中..."; kill $SERVER_PID 2>/dev/null; rm -f server.pid; echo "✅ サーバーを停止しました"; exit 0' INT

# サーバーが終了するまで待機
wait $SERVER_PID