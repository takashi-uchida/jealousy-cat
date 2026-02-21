#!/bin/bash
# threaten_process.sh
# アクティビティモニタを起動し、プロセスを強制終了するような警告ダイアログを出す

echo "☠️ プロセス終了の警告を出します..."
osascript <<EOF
tell application "Activity Monitor"
    activate
end tell
delay 1
tell application "System Events"
    display dialog "ユーザーの意識が他の対象（猫A）に極度に逸れています。\nタスクに集中していないため、無関係なプロセスを強制終了しますか？" buttons {"やめて！", "強制終了する"} default button "やめて！" with icon caution with title "Jealousy System Alert"
end tell
EOF
