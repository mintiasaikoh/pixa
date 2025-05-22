#!/bin/bash

# AI ピクセルアート ジェネレーター サーバー停止スクリプト

echo "🛑 AI ピクセルアート ジェネレーター を停止中..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# PIDファイルが存在する場合、プロセスを停止
if [ -f "server.pid" ]; then
    SERVER_PID=$(cat server.pid)
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "🔧 統合サーバー (PID: $SERVER_PID) を停止中..."
        kill $SERVER_PID
    fi
    rm -f server.pid
fi

# ポートを使用しているプロセスも強制終了
echo "🧹 残留プロセスをクリーンアップ中..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

echo "✅ サーバーを停止しました"