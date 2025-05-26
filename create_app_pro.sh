#!/bin/bash

# Pixa Pro.app作成スクリプト
# より高度なmacOSアプリケーションバンドルを作成

echo "🎨 Pixa Pro.appを作成します（バックグラウンド起動版）..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# アプリケーションディレクトリ構造を作成
APP_NAME="Pixa Pro"
APP_DIR="${APP_NAME}.app"

echo "📁 アプリケーション構造を作成中..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# 実行可能スクリプトを作成
cat > "$APP_DIR/Contents/MacOS/pixa_launcher" << 'EOF'
#!/bin/bash

# Pixaアプリケーションランチャー
# バックグラウンドでサーバーを起動し、ブラウザで開く

# アプリケーションのパスを取得
APP_PATH="$(cd "$(dirname "$0")/../../../.." && pwd)"

# ログファイルの設定
LOG_DIR="$HOME/Library/Logs/Pixa"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/pixa.log"

# ログ関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "===== Pixa起動開始 ====="
log "アプリケーションパス: $APP_PATH"

# 既存のPixaプロセスをチェック
if pgrep -f "python.*server.py" > /dev/null; then
    log "Pixaサーバーは既に起動しています"
    # ブラウザで開く
    open "http://localhost:5001"
    exit 0
fi

# Pixaディレクトリに移動
cd "$APP_PATH" || {
    log "エラー: Pixaディレクトリが見つかりません"
    osascript -e 'display alert "エラー" message "Pixaディレクトリが見つかりません。" as critical'
    exit 1
}

# Python仮想環境の確認
if [ ! -d "venv" ]; then
    log "Python仮想環境を作成中..."
    /usr/bin/python3 -m venv venv >> "$LOG_FILE" 2>&1
fi

# 仮想環境をアクティベート
source venv/bin/activate >> "$LOG_FILE" 2>&1

# 依存関係のインストール（必要な場合）
if [ ! -f "venv/.deps_installed" ]; then
    log "依存関係をインストール中..."
    pip install -r backend/requirements.txt >> "$LOG_FILE" 2>&1
    touch "venv/.deps_installed"
fi

# サーバーをバックグラウンドで起動
log "サーバーを起動中..."
cd backend
nohup python server.py >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$APP_PATH/server.pid"

log "サーバーPID: $SERVER_PID"

# サーバーの起動を待つ
echo "サーバーの起動を待っています..."
for i in {1..30}; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        log "サーバーが起動しました"
        break
    fi
    sleep 1
done

# ブラウザで開く
log "ブラウザでPixaを開いています..."
open "http://localhost:5001"

# 起動完了通知（オプション）
osascript -e 'display notification "Pixaが起動しました" with title "Pixa"' 2>/dev/null

log "===== Pixa起動完了 ====="
EOF

# 実行権限を付与
chmod +x "$APP_DIR/Contents/MacOS/pixa_launcher"

# Info.plistを作成
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Pixa Pro</string>
    <key>CFBundleDisplayName</key>
    <string>Pixa Pro - AI Pixel Art Generator</string>
    <key>CFBundleIdentifier</key>
    <string>com.pixa.pro</string>
    <key>CFBundleVersion</key>
    <string>2.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>CFBundleExecutable</key>
    <string>pixa_launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>PIXA</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# デフォルトアイコンを作成（簡易版）
if ! [ -f "AppIcon.icns" ]; then
    echo "🎨 デフォルトアイコンを作成中..."
    # 簡易的なアイコンを作成
    cat > create_icon.py << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import os

# アイコン画像を作成（512x512）
size = 512
img = Image.new('RGB', (size, size), '#0f0f0f')
draw = ImageDraw.Draw(img)

# グラデーション背景
for i in range(size):
    color = int(15 + (40 * i / size))
    draw.rectangle([0, i, size, i+1], fill=(color, color, color))

# ピクセルアートスタイルの"P"
pixel_size = 32
p_pattern = [
    [1,1,1,1,1,0],
    [1,0,0,0,1,0],
    [1,0,0,0,1,0],
    [1,1,1,1,1,0],
    [1,0,0,0,0,0],
    [1,0,0,0,0,0],
    [1,0,0,0,0,0]
]

start_x = size // 2 - len(p_pattern[0]) * pixel_size // 2
start_y = size // 2 - len(p_pattern) * pixel_size // 2

for y, row in enumerate(p_pattern):
    for x, pixel in enumerate(row):
        if pixel:
            draw.rectangle([
                start_x + x * pixel_size,
                start_y + y * pixel_size,
                start_x + (x + 1) * pixel_size,
                start_y + (y + 1) * pixel_size
            ], fill='#00ff41')

# 画像を保存
img.save('icon_512.png')
print("アイコンが作成されました")
EOF

    if command -v python3 >/dev/null 2>&1 && python3 -c "import PIL" 2>/dev/null; then
        python3 create_icon.py
        # PNGをICNSに変換（macOS標準ツール使用）
        if [ -f "icon_512.png" ]; then
            mkdir icon.iconset
            cp icon_512.png icon.iconset/icon_512x512.png
            sips -z 256 256 icon_512.png --out icon.iconset/icon_256x256.png 2>/dev/null
            sips -z 128 128 icon_512.png --out icon.iconset/icon_128x128.png 2>/dev/null
            sips -z 64 64 icon_512.png --out icon.iconset/icon_64x64.png 2>/dev/null
            sips -z 32 32 icon_512.png --out icon.iconset/icon_32x32.png 2>/dev/null
            sips -z 16 16 icon_512.png --out icon.iconset/icon_16x16.png 2>/dev/null
            iconutil -c icns icon.iconset -o AppIcon.icns 2>/dev/null
            rm -rf icon.iconset icon_512.png
        fi
        rm create_icon.py
    fi
fi

# アイコンをコピー
if [ -f "AppIcon.icns" ]; then
    cp AppIcon.icns "$APP_DIR/Contents/Resources/AppIcon.icns"
fi

# 停止スクリプトも作成
cat > stop_pixa.sh << 'EOF'
#!/bin/bash
# Pixaサーバーを停止

if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Pixaサーバーを停止中..."
        kill $PID
        rm server.pid
        echo "✅ Pixaサーバーが停止しました"
    else
        echo "Pixaサーバーは実行されていません"
    fi
else
    # pidファイルがない場合はプロセス名で検索
    if pgrep -f "python.*server.py" > /dev/null; then
        echo "Pixaサーバーを停止中..."
        pkill -f "python.*server.py"
        echo "✅ Pixaサーバーが停止しました"
    else
        echo "Pixaサーバーは実行されていません"
    fi
fi
EOF
chmod +x stop_pixa.sh

echo "✅ ${APP_NAME}.appが作成されました！"
echo ""
echo "📌 使い方:"
echo "1. ${APP_NAME}.appをApplicationsフォルダに移動（推奨）"
echo "   mv \"${APP_NAME}.app\" /Applications/"
echo ""
echo "2. ${APP_NAME}.appをダブルクリックで起動"
echo ""
echo "3. サーバーを停止するには:"
echo "   ./stop_pixa.sh"
echo ""
echo "📁 ログファイルの場所:"
echo "   ~/Library/Logs/Pixa/pixa.log"
echo ""
echo "⚠️  注意:"
echo "- 初回起動時はセキュリティ警告が出る場合があります"
echo "- システム環境設定 > セキュリティとプライバシー で許可してください"
echo "- アプリはバックグラウンドでサーバーを起動します"
