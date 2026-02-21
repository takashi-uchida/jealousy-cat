#!/bin/bash
# terminal_ghost.sh
# ターミナルに勝手に大量のテキストを出力するか、新規ターミナルを立ち上げる

echo "👻 システム内部からメッセージを送信します..."

osascript -e '
tell application "Terminal"
    activate
    do script "echo \"Jealousy.sys: Do you think you can just ignore me?\"; sleep 1; echo \"Jealousy.sys: I am the one running this machine.\"; sleep 1; for i in {1..5}; do echo \"LOOK AT ME\"; sleep 0.2; done"
end tell'
