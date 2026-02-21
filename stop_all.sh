#!/bin/bash
# stop_all.sh
# Jealousy.sys に関連するすべての音声・ゲームプロセスを強制終了する

echo "🛑 Jealousy.sys の全プロセスを停止しています..."

# 1. 音声再生プロセス
pkill -9 -f "afplay" 2>/dev/null
pkill -9 -f "say " 2>/dev/null

# 2. BGMループスクリプト
pkill -9 -f "play_bgm.sh" 2>/dev/null

# 3. ゲーム本体プロセス
pkill -9 -f "native_game.py" 2>/dev/null
pkill -9 -f "game_server.py" 2>/dev/null
pkill -9 -f "main_loop.py" 2>/dev/null

# 4. センサープロセス
pkill -9 -f "active_window_sensor.py" 2>/dev/null
pkill -9 -f "vision_sensor.py" 2>/dev/null

# 5. PIDファイルのクリーンアップ
rm /tmp/jealousy_bgm_*.pid 2>/dev/null
rm .reconcile_request 2>/dev/null
rm .game_state.json 2>/dev/null

echo "✨ すべてのプロセスをクリーンアップしました。音は止まったはずです。"
