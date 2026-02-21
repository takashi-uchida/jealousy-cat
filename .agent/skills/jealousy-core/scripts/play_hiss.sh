#!/bin/bash
# play_hiss.sh
# macOSのsayコマンドを使って、威嚇する声や唸り声のような音声を合成して再生します

# ランダムで音声を切り替える
RANDOM_NUM=$((1 + $RANDOM % 3))

echo "🔊 音声を再生します..."

case $RANDOM_NUM in
  1)
    # 低くて重い声 (Zarvox 等のロボットボイスを使用)
    osascript -e 'set volume output volume 80'
    say -v Zarvox "Ggrrrrrrrrrr"
    ;;
  2)
    # 囁くような声 (Whisper 等) 
    osascript -e 'set volume output volume 80'
    say -v Whisper "I am looking at you"
    ;;
  3)
    # 悲しげな声 (Bells 等の特殊効果)
    osascript -e 'set volume output volume 80'
    say -v Bells "Look at me"
    ;;
esac
