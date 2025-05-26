#!/bin/bash

# Pixa.app作成スクリプト
# macOS用のアプリケーションバンドルを作成

echo "🎨 Pixa.appを作成します..."

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# AppleScriptコードを作成
cat > pixa_launcher.applescript << 'EOF'
on run
    -- Pixaプロジェクトのパスを設定（ユーザーのパスに合わせて変更）
    set pixaPath to "/Users/mymac/pixa"
    
    -- ターミナルでstart_server.shを実行
    tell application "Terminal"
        -- 新しいウィンドウを作成
        do script "cd " & quoted form of pixaPath & " && ./start_server.sh"
        activate
    end tell
    
    -- 少し待ってからブラウザを開く
    delay 5
    
    -- デフォルトブラウザでPixaを開く
    do shell script "open http://localhost:5001"
end run
EOF

# AppleScriptをコンパイルして.appを作成
echo "📦 AppleScriptをコンパイル中..."
osacompile -o Pixa.app pixa_launcher.applescript

# アイコンを設定（オプション）
if [ -f "icon.icns" ]; then
    echo "🎨 アイコンを設定中..."
    cp icon.icns Pixa.app/Contents/Resources/applet.icns
fi

# Info.plistをカスタマイズ
cat > Pixa.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Pixa</string>
    <key>CFBundleDisplayName</key>
    <string>Pixa - AI Pixel Art Generator</string>
    <key>CFBundleIdentifier</key>
    <string>com.pixa.launcher</string>
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
rm pixa_launcher.applescript

echo "✅ Pixa.appが作成されました！"
echo ""
echo "📌 使い方:"
echo "1. Pixa.appをApplicationsフォルダに移動（オプション）"
echo "   mv Pixa.app /Applications/"
echo ""
echo "2. Pixa.appをダブルクリックで起動"
echo ""
echo "⚠️  注意: 初回起動時はセキュリティ警告が出る場合があります。"
echo "   システム環境設定 > セキュリティとプライバシー で許可してください。"
