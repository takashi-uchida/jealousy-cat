#!/bin/bash
# toggle_dark_mode.sh
# 感情の高ぶりに合わせて、勝手にダークモード／ライトモードを切り替えて画面全体をチカチカさせる

echo "🌗 システムテーマを反転させて画面をチカチカさせます..."

for i in {1..6}; do
    osascript -e '
    tell application "System Events"
        tell appearance preferences
            set dark mode to not dark mode
        end tell
    end tell'
    sleep 0.5
done
