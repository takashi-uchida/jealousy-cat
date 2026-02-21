#!/bin/bash
# change_cursor.sh
# macOSのマウスカーソルサイズを変更して、OSが干渉してきている感を強調する

if [ "$1" == "reset" ]; then
    echo "🔄 マウスカーソルを元のサイズに戻します"
    defaults write com.apple.universalaccess mouseDriverCursorSize 1.0
else
    echo "🖱 マウスカーソルを巨大化させます（自己主張）"
    defaults write com.apple.universalaccess mouseDriverCursorSize 3.0
fi

# 変更を適用するにはSystemUIServerなどを再起動する必要がある場合がありますが、
# 近年のmacOSではこれだけではリアルタイム反映されないため、補助的な演出として利用します。
# 確実なOSジャック感のために、Dockを再起動して画面を一瞬リフレッシュさせます。
killall Dock
echo "⚡ Dockをリロードしました"
