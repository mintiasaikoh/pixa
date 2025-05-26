#!/bin/bash
# Pixaサーバーを停止

echo "🛑 Pixaサーバーを停止中..."

# server.pidファイルを探す
PID_FILE=$(find "$HOME" -name 'server.pid' -path '*/pixa/*' 2>/dev/null | head -1)

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        rm "$PID_FILE"
        echo "✅ Pixaサーバーが停止しました (PID: $PID)"
    else
        echo "⚠️ Pixaサーバーは実行されていません (古いPIDファイルを削除)"
        rm "$PID_FILE"
    fi
else
    # pidファイルがない場合はプロセス名で検索
    if pgrep -f "python.*server.py" > /dev/null; then
        pkill -f "python.*server.py"
        echo "✅ Pixaサーバーが停止しました"
    else
        echo "ℹ️ Pixaサーバーは実行されていません"
    fi
fi

# 通知を表示
osascript -e 'display notification "Pixaサーバーが停止しました" with title "Pixa"' 2>/dev/null

echo ""
echo "このウィンドウは閉じて構いません。"
