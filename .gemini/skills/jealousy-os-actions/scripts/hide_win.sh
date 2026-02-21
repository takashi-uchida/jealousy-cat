#!/bin/bash
# hide_win.sh
# ユーザーが現在見ている最前面のアプリのウィンドウを隠す (Cmd + H)

echo "🙈 最前面のウィンドウを隠します..."
osascript -e 'tell application "System Events" to keystroke "h" using command down'
