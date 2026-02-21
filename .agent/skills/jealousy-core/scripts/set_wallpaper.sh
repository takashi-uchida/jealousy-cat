#!/bin/bash
# set_wallpaper.sh
# 指定された画像をmacOSの壁紙として設定するスクリプト

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <absolute_path_to_image>"
    exit 1
fi

IMAGE_PATH=$1

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Error: File not found -> $IMAGE_PATH"
    exit 1
fi

echo "🖼 壁紙を和解の画像に変更します..."

# AppleScriptを使用して壁紙を変更 (複数ディスプレイ対応)
osascript -e "tell application \"System Events\"
    set desktopCount to count of desktops
    repeat with desktopNumber from 1 to desktopCount
        tell desktop desktopNumber
            set picture to \"$IMAGE_PATH\"
        end tell
    end repeat
end tell"

echo "✅ 壁紙のが変更されました。"
