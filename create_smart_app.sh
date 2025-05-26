#!/bin/bash

# Pixa Smart.app作成スクリプト
# 自動的にPixaプロジェクトを検出してダブルクリックで起動

echo "🎨 Pixa Smart.appを作成します（自動検出版）..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# アプリケーションディレクトリ構造を作成
APP_NAME="Pixa"
APP_DIR="${APP_NAME}.app"

echo "📁 アプリケーション構造を作成中..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# 実行可能スクリプトを作成
cat > "$APP_DIR/Contents/MacOS/pixa_smart_launcher" << 'EOF'
#!/bin/bash

# Pixa Smart Launcher - 自動検出版
# Pixaプロジェクトを自動的に見つけて起動

# ログ設定
LOG_DIR="$HOME/Library/Logs/Pixa"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/pixa_smart.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 通知を表示
notify() {
    osascript -e "display notification \"$1\" with title \"Pixa\""
}

log "===== Pixa Smart Launcher 起動 ====="

# Pixaプロジェクトを検索
find_pixa_project() {
    local search_paths=(
        "$HOME/pixa"
        "$HOME/Desktop/pixa"
        "$HOME/Documents/pixa"
        "$HOME/Projects/pixa"
        "$HOME/Developer/pixa"
        "$HOME/Code/pixa"
        "/Users/$(whoami)/pixa"
        "$(dirname "$0")/../../../.."
    )
    
    log "Pixaプロジェクトを検索中..."
    
    for path in "${search_paths[@]}"; do
        if [ -d "$path" ] && [ -f "$path/start_server.sh" ]; then
            log "✅ Pixaプロジェクトを発見: $path"
            echo "$path"
            return 0
        fi
    done
    
    # 見つからない場合は、modelsディレクトリを持つPixaプロジェクトを広く検索
    log "より広範囲で検索中..."
    local found_path=$(find "$HOME" -type d -name "pixa" -not -path "*/.*" 2>/dev/null | while read dir; do
        if [ -f "$dir/start_server.sh" ] || [ -d "$dir/models" ] || [ -f "$dir/backend/server.py" ]; then
            echo "$dir"
            break
        fi
    done | head -1)
    
    if [ -n "$found_path" ]; then
        log "✅ Pixaプロジェクトを発見: $found_path"
        echo "$found_path"
        return 0
    fi
    
    return 1
}

# モデルファイルの確認
check_models() {
    local pixa_path="$1"
    local models_dir="$pixa_path/models"
    
    if [ -d "$models_dir" ]; then
        local model_count=$(find "$models_dir" -type f -name "*.safetensors" -o -name "*.ckpt" -o -name "*.bin" 2>/dev/null | wc -l)
        log "📦 モデルファイル数: $model_count"
        
        if [ $model_count -gt 0 ]; then
            log "✅ モデルファイルが見つかりました"
            return 0
        else
            log "⚠️ モデルファイルが見つかりません（初回起動時に自動ダウンロード）"
            return 1
        fi
    else
        log "📁 modelsディレクトリが存在しません（初回起動時に作成）"
        return 1
    fi
}

# メインプロセス
main() {
    # 既存のPixaプロセスをチェック
    if pgrep -f "python.*server.py" > /dev/null; then
        log "Pixaサーバーは既に起動しています"
        notify "Pixaは既に起動しています"
        open "http://localhost:5001"
        exit 0
    fi
    
    # Pixaプロジェクトを検索
    PIXA_PATH=$(find_pixa_project)
    
    if [ -z "$PIXA_PATH" ]; then
        log "❌ Pixaプロジェクトが見つかりません"
        osascript -e 'display alert "Pixaプロジェクトが見つかりません" message "Pixaプロジェクトフォルダを確認してください。\n一般的な場所:\n• ~/pixa\n• ~/Desktop/pixa\n• ~/Documents/pixa" as critical'
        exit 1
    fi
    
    # モデルファイルの確認
    check_models "$PIXA_PATH"
    
    # プロジェクトディレクトリに移動
    cd "$PIXA_PATH" || {
        log "❌ ディレクトリへの移動に失敗"
        exit 1
    }
    
    # サーバー起動方法を選択
    if [ -f "start_server.sh" ]; then
        log "📜 start_server.shを使用して起動"
        # ターミナルで起動（ログが見える）
        osascript -e "tell application \"Terminal\"
            do script \"cd \\\"$PIXA_PATH\\\" && ./start_server.sh\"
            activate
        end tell"
    else
        log "🐍 直接Pythonサーバーを起動"
        # Python仮想環境の確認
        if [ ! -d "venv" ]; then
            log "Python仮想環境を作成中..."
            python3 -m venv venv
        fi
        
        # 仮想環境をアクティベート
        source venv/bin/activate
        
        # 依存関係のインストール
        if [ ! -f "venv/.deps_installed" ]; then
            log "依存関係をインストール中..."
            pip install -r backend/requirements.txt
            touch "venv/.deps_installed"
        fi
        
        # サーバーをバックグラウンドで起動
        cd backend
        nohup python server.py >> "$LOG_FILE" 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > "$PIXA_PATH/server.pid"
        
        # サーバーの起動を待つ
        log "サーバーの起動を待っています..."
        for i in {1..30}; do
            if curl -s http://localhost:5001/health > /dev/null 2>&1; then
                log "✅ サーバーが起動しました"
                break
            fi
            sleep 1
        done
        
        # ブラウザで開く
        open "http://localhost:5001"
    fi
    
    notify "Pixaが起動しました"
    log "===== Pixa起動完了 ====="
}

# エラーハンドリング
trap 'log "エラーが発生しました: $?"' ERR

# メイン処理を実行
main
EOF

# 実行権限を付与
chmod +x "$APP_DIR/Contents/MacOS/pixa_smart_launcher"

# Info.plistを作成
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Pixa</string>
    <key>CFBundleDisplayName</key>
    <string>Pixa - AI Pixel Art Generator</string>
    <key>CFBundleIdentifier</key>
    <string>com.pixa.smart</string>
    <key>CFBundleVersion</key>
    <string>3.0</string>
    <key>CFBundleShortVersionString</key>
    <string>3.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>CFBundleExecutable</key>
    <string>pixa_smart_launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>PIXA</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# アイコンの作成
echo "🎨 アイコンを作成中..."
cat > create_pixa_icon.py << 'EOF'
#!/usr/bin/env python3
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PILがインストールされていないため、デフォルトアイコンを使用します")
    sys.exit(0)

# アイコン画像を作成（512x512）
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 背景（角丸四角形）
def draw_rounded_rect(draw, coords, radius, fill):
    x1, y1, x2, y2 = coords
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+2*radius, y1+2*radius], 180, 270, fill=fill)
    draw.pieslice([x2-2*radius, y1, x2, y1+2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2-2*radius, x1+2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*radius, y2-2*radius, x2, y2], 0, 90, fill=fill)

# 背景グラデーション
draw_rounded_rect(draw, [20, 20, 492, 492], 50, '#1a1a1a')

# ピクセルアートパターン
pixel_size = 24
colors = ['#00ff41', '#ff0080', '#ffff00', '#00b8ff']
pattern = [
    [0, 1, 1, 0, 0, 2, 2, 0],
    [1, 0, 0, 1, 2, 0, 0, 2],
    [1, 0, 0, 1, 2, 0, 0, 2],
    [0, 1, 1, 0, 0, 2, 2, 0],
    [3, 0, 0, 3, 0, 1, 1, 0],
    [0, 3, 3, 0, 1, 0, 0, 1],
    [0, 3, 3, 0, 1, 0, 0, 1],
    [3, 0, 0, 3, 0, 1, 1, 0]
]

# パターンを中央に配置
start_x = size // 2 - len(pattern[0]) * pixel_size // 2
start_y = size // 2 - len(pattern) * pixel_size // 2

for y, row in enumerate(pattern):
    for x, color_idx in enumerate(row):
        if color_idx > 0:
            color = colors[color_idx - 1]
            draw.rectangle([
                start_x + x * pixel_size,
                start_y + y * pixel_size,
                start_x + (x + 1) * pixel_size - 2,
                start_y + (y + 1) * pixel_size - 2
            ], fill=color)

# "PIXA"テキスト（ピクセルフォント風）
text_y = start_y + len(pattern) * pixel_size + 40
text = "PIXA"
text_size = 48
for i, char in enumerate(text):
    x = size // 2 - len(text) * text_size // 2 + i * text_size
    # 簡易的なピクセルフォント
    draw.rectangle([x, text_y, x + text_size - 8, text_y + text_size], fill='#00ff41')

# 画像を保存
img.save('pixa_icon_512.png')

# 各サイズのアイコンを作成
sizes = [512, 256, 128, 64, 32, 16]
os.makedirs('pixa.iconset', exist_ok=True)

for s in sizes:
    resized = img.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(f'pixa.iconset/icon_{s}x{s}.png')
    # Retinaディスプレイ用
    if s <= 256:
        resized_2x = img.resize((s*2, s*2), Image.Resampling.LANCZOS)
        resized_2x.save(f'pixa.iconset/icon_{s}x{s}@2x.png')

print("✅ アイコンファイルが作成されました")
EOF

# Pythonでアイコンを作成
if command -v python3 >/dev/null 2>&1; then
    python3 create_pixa_icon.py 2>/dev/null || echo "⚠️ カスタムアイコンの作成をスキップ"
    
    # ICNSファイルに変換
    if [ -d "pixa.iconset" ]; then
        iconutil -c icns pixa.iconset -o "$APP_DIR/Contents/Resources/AppIcon.icns" 2>/dev/null || \
        echo "⚠️ アイコン変換をスキップ"
        rm -rf pixa.iconset pixa_icon_512.png create_pixa_icon.py
    fi
fi

# メニューバー停止スクリプトも作成
cat > "Stop Pixa.app/Contents/MacOS/stop_pixa" << 'EOF'
#!/bin/bash
# Pixaを停止
if [ -f "$HOME/pixa/server.pid" ] || [ -f "$(find $HOME -name 'server.pid' -path '*/pixa/*' 2>/dev/null | head -1)" ]; then
    PID_FILE=$(find $HOME -name 'server.pid' -path '*/pixa/*' 2>/dev/null | head -1)
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID 2>/dev/null
        rm "$PID_FILE"
    fi
fi
pkill -f "python.*server.py" 2>/dev/null
osascript -e 'display notification "Pixaサーバーが停止しました" with title "Pixa"'
EOF

mkdir -p "Stop Pixa.app/Contents/MacOS"
chmod +x "Stop Pixa.app/Contents/MacOS/stop_pixa"

echo "✅ Pixa.appが作成されました！"
echo ""
echo "🚀 特徴:"
echo "• Pixaプロジェクトを自動検出"
echo "• モデルファイルの存在を確認"
echo "• ダブルクリックで起動"
echo "• ログは ~/Library/Logs/Pixa/ に保存"
echo ""
echo "📁 使い方:"
echo "1. Pixa.appをApplicationsフォルダに移動"
echo "   mv Pixa.app /Applications/"
echo ""
echo "2. ダブルクリックで起動！"
echo ""
echo "🛑 停止方法:"
echo "• Stop Pixa.appをダブルクリック"
echo "• または ./stop_pixa.sh を実行"
