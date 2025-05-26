#!/bin/bash

# Pixa Desktop.app作成スクリプト
# Pygameデスクトップ版用のmacOSアプリケーション

echo "🎮 Pixa Desktop.appを作成します（Pygame版）..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# AppleScriptコードを作成
cat > pixa_desktop_launcher.applescript << 'EOF'
on run
    -- Pixaプロジェクトのパスを設定
    set pixaPath to "/Users/mymac/pixa"
    
    -- ターミナルでpygame版を起動
    tell application "Terminal"
        -- 新しいウィンドウを作成
        do script "cd " & quoted form of pixaPath & " && ./start_pygame.sh"
        
        -- ターミナルウィンドウを前面に
        activate
    end tell
end run
EOF

# AppleScriptをコンパイルして.appを作成
echo "📦 AppleScriptをコンパイル中..."
osacompile -o "Pixa Desktop.app" pixa_desktop_launcher.applescript

# Info.plistをカスタマイズ
cat > "Pixa Desktop.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Pixa Desktop</string>
    <key>CFBundleDisplayName</key>
    <string>Pixa Desktop - Pygame Version</string>
    <key>CFBundleIdentifier</key>
    <string>com.pixa.desktop</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>CFBundleIconFile</key>
    <string>applet</string>
    <key>CFBundleExecutable</key>
    <string>applet</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>aplt</string>
</dict>
</plist>
EOF

# 一時ファイルを削除
rm pixa_desktop_launcher.applescript

echo "✅ Pixa Desktop.appが作成されました！"
echo ""
echo "使い方: Pixa Desktop.appをダブルクリックで起動"
