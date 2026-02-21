#!/bin/bash
# play_bgm.sh
# afplay を使ってBGMをループ再生するスクリプト

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 start/stop <mode(healing|jealous)>"
    exit 1
fi

ACTION=$1
MODE=$2

# モードごとに別々のPIDファイルを使う
BGM_PID_FILE="/tmp/jealousy_bgm_${MODE}.pid"

if [ "$ACTION" == "stop" ]; then
    if [ -f "$BGM_PID_FILE" ]; then
        PID=$(cat "$BGM_PID_FILE")
        # 該当PIDとその子プロセスをkill
        kill -9 "$PID" 2>/dev/null
        pkill -P "$PID" 2>/dev/null
        rm "$BGM_PID_FILE"
        echo "🛑 ${MODE} BGMを停止しました"
    fi
    # PIDファイルがなくても、afplayプロセスを名前で念のり止める
    pkill -f "afplay" 2>/dev/null || true
    exit 0
fi

if [ "$ACTION" == "start" ]; then
    # すでに再生中なら一旦止める
    $0 stop "$MODE"

    if [ "$MODE" == "healing" ]; then
        # 癒やし系WebアプリのBGMとして、macOS標準の穏やかな環境音や音色を生成してごまかす（外部mp3不要）
        echo "🎶 Healing BGMを開始します..."
        (
            while true; do
                osascript -e 'set volume output volume 30'
                # 穏やかな鈴の音をゆっくり連続再生
                for i in {1..3}; do afplay /System/Library/Sounds/Glass.aiff; sleep 1; done
                sleep 2
                afplay /System/Library/Sounds/Tink.aiff
                sleep 5
            done
        ) &
        echo $! > "$BGM_PID_FILE"
        
    elif [ "$MODE" == "jealous" ]; then
        # 嫉妬モードの猫っぽい不穏なBGM
        echo "🚨 Jealous BGMを開始します...（猫モード）"
        (
            while true; do
                osascript -e 'set volume output volume 60'
                # 猫の唸り（Purr = ゴロゴロ怒り）
                afplay /System/Library/Sounds/Purr.aiff
                sleep 0.3
                # 猫パンチ（Pop = パシッ）
                afplay /System/Library/Sounds/Pop.aiff
                sleep 0.2
                afplay /System/Library/Sounds/Pop.aiff
                sleep 0.8
                # 不満の唸り
                afplay /System/Library/Sounds/Purr.aiff
                sleep 0.5
                # たまに威嚇音（Funk = フーッ的な）
                if (( RANDOM % 3 == 0 )); then
                    afplay /System/Library/Sounds/Funk.aiff
                    sleep 0.3
                fi
                sleep 2
            done
        ) &
        echo $! > "$BGM_PID_FILE"
    fi
fi

