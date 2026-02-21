#!/usr/bin/env python3
# game_server.py
# Jealousy.sys — ゲームサーバー
# Web UIとバックエンド（嫉妬ロジック + OS干渉スクリプト）を接続するHTTPサーバー

import os
import sys
import json
import time
import random
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web-app")
SCRIPTS_DIR = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "scripts")

# ── スクリプトパス ──
CHAOTIC_MOUSE = os.path.join(SCRIPTS_DIR, "chaotic_mouse.swift")
HIDE_WIN = os.path.join(SCRIPTS_DIR, "hide_win.sh")
THREATEN_PROC = os.path.join(SCRIPTS_DIR, "threaten_process.sh")
TYPE_MSG = os.path.join(SCRIPTS_DIR, "type_msg.py")
PLAY_HISS = os.path.join(SCRIPTS_DIR, "play_hiss.sh")
WHISPER = os.path.join(SCRIPTS_DIR, "random_whisper.py")
SET_WALLPAPER = os.path.join(SCRIPTS_DIR, "set_wallpaper.sh")
ROAMING_CAT = os.path.join(SCRIPTS_DIR, "roaming_cat.py")
CAT_TOAST = os.path.join(SCRIPTS_DIR, "cat_toast.py")
TOGGLE_THEME = os.path.join(SCRIPTS_DIR, "os_hacks", "toggle_dark_mode.sh")
TERMINAL_GHOST = os.path.join(SCRIPTS_DIR, "os_hacks", "terminal_ghost.sh")
PLAY_BGM = os.path.join(SCRIPTS_DIR, "play_bgm.sh")
GENERATE_WALLPAPER = os.path.join(SCRIPTS_DIR, "generate_wallpaper.py")
RECONCILIATION_IMG = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "assets", "reconciliation.png")


# ══════════════════════════════════════════
# ゲーム状態 (共有オブジェクト)
# ══════════════════════════════════════════
class GameState:
    """ゲームの全状態を管理するシングルトン"""

    # 嫉妬猫のセリフ集（レベル別）
    DIALOGUES = {
        "calm": [
            "...ふぅん、まぁいいけど。",
            "（こっちをチラッと見ている）",
            "...別に寂しくないし。",
            "zzz... zzz...",
            "（しっぽをゆらゆら揺らしている）",
        ],
        "annoyance": [
            "...ねぇ、ボクのこと見えてる？",
            "その子ばっかりナデナデするじゃん...！",
            "ちょっと...無視しないでよ...",
            "（イライラしてしっぽを叩きつけている）",
            "ボクだってナデナデされたいニャ...",
            "PCの操作、ちょっと邪魔してやるニャ～",
        ],
        "obsession": [
            "もう許さないんだから！！",
            "ボクを置いて他の猫と...信じられない！",
            "ウィンドウ？隠しちゃお♪",
            "画面の色、変えちゃうよ？ネ？",
            "ボクが画面を歩いてやるニャ！！",
            "...もう限界かも。ボク、壊れちゃうかも。",
        ],
        "rage": [
            "ボクだけを見て...お願いだから...",
            "もう...全部消しちゃおうかな...",
            "最後のチャンスだよ？ねぇ...？",
            "ターミナルから...お前のプロセスを...",
            "💀 ...ボクを怒らせたね？",
            "さよなら...って言いたくないのに...",
        ],
        "max": [
            "...もう、限界。",
            "最後に一つだけ聞いて。ボクのこと...好き？",
            "謝ってくれたら...許してあげてもいいよ？",
        ],
    }

    # 和解成功時の判定キーワード
    RECONCILE_KEYWORDS = [
        "好き", "大好き", "ごめん", "ごめんね", "すき", "一番",
        "かわいい", "可愛い", "大切", "愛してる", "許して",
        "ごめんなさい", "仲直り", "love", "sorry",
        "なでなで", "よしよし", "いい子", "構ってあげる",
    ]

    def __init__(self):
        self.jealousy_level = 0
        self.pets_count = 0
        self.game_phase = "intro"  # intro | playing | reconciling | ending
        self.events = []
        self.cat_dialogue = "..."
        self.last_action_time = 0
        self.os_actions_enabled = True
        self.lock = threading.Lock()

    def get_stage(self):
        if self.jealousy_level < 20:
            return "calm", "😺 平穏"
        elif self.jealousy_level < 50:
            return "annoyance", "😾 イライラ"
        elif self.jealousy_level < 80:
            return "obsession", "🙀 執着"
        elif self.jealousy_level < 100:
            return "rage", "😈 暴走"
        else:
            return "max", "💀 限界突破"

    def add_event(self, event_text):
        with self.lock:
            self.events.append({
                "text": event_text,
                "time": datetime.now().strftime("%H:%M:%S"),
            })
            # 最大20件保持
            if len(self.events) > 20:
                self.events = self.events[-20:]

    def update_dialogue(self):
        stage, _ = self.get_stage()
        candidates = self.DIALOGUES.get(stage, self.DIALOGUES["calm"])
        self.cat_dialogue = random.choice(candidates)

    def to_dict(self):
        stage, stage_name = self.get_stage()
        return {
            "jealousy_level": min(self.jealousy_level, 100),
            "stage": stage,
            "stage_name": stage_name,
            "events": self.events[-10:],  # 直近10件
            "cat_dialogue": self.cat_dialogue,
            "game_phase": self.game_phase,
            "pets_count": self.pets_count,
        }


# グローバルゲーム状態
game = GameState()


# ══════════════════════════════════════════
# OS干渉アクション
# ══════════════════════════════════════════
def run_script(script_path, args=None, async_mode=True):
    """ワーカースクリプトを実行"""
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return
    cmd = [script_path]
    if script_path.endswith(".py"):
        cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    try:
        if async_mode:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Script error: {e}")


def _toast(level_key, message):
    """macOS通知トーストを非同期で表示"""
    run_script(CAT_TOAST, [level_key, message])


def trigger_os_action(level):
    """嫉妬レベルに応じたOS干渉を実行"""
    if not game.os_actions_enabled:
        return

    now = time.time()
    if now - game.last_action_time < 5:  # クールダウン 5秒
        return
    game.last_action_time = now

    if 20 <= level < 50:
        actions = [
            ("🖱️ マウスが勝手に動き出した！", CHAOTIC_MOUSE, [], "1", "マウスを揺らしてやるニャ"),
            ("😾 「シャーッ！」と威嚇された！", PLAY_HISS, [], "1", "警告だニャ"),
        ]
        action = random.choice(actions)
        game.add_event(action[0])
        run_script(action[1], action[2] or None)
        _toast(action[3], action[4])

    elif 50 <= level < 80:
        actions = [
            ("🪟 ウィンドウが勝手に隠された！", HIDE_WIN, [], "2", "邪魔してやるニャ"),
            ("🌗 画面のテーマが反転した！", TOGGLE_THEME, [], "2", "世界を暗くしてやるニャ"),
            ("🐈‍⬛ 黒猫が画面を徘徊し始めた！", ROAMING_CAT, [], "2", "ボクを見てニャ！"),
        ]
        action = random.choice(actions)
        game.add_event(action[0])
        run_script(action[1], action[2] or None)
        _toast(action[3], action[4])

    elif 80 <= level < 100:
        actions = [
            ("👻 ターミナルに不気味な文字が...！", TERMINAL_GHOST, [], "3", "呪いをかけてやるニャ"),
            ("📝 テキストエディタに何か書かれている...", TYPE_MSG, [], "3", "気持ちを伝えるニャ"),
        ]
        action = random.choice(actions)
        game.add_event(action[0])
        run_script(action[1], action[2] or None)
        _toast(action[3], action[4])

    elif level >= 100:
        game.add_event("💀 プロセスの強制終了を脅迫された！！")
        _toast("MAX", "もう我慢できないニャ！")
        run_script(THREATEN_PROC)
        game.game_phase = "reconciling"


def try_reconcile(text):
    """和解テキストを判定"""
    text_lower = text.lower()
    score = 0
    for keyword in GameState.RECONCILE_KEYWORDS:
        if keyword in text_lower:
            score += 1

    if score >= 1:
        # 和解成功！
        game.jealousy_level = 0
        game.pets_count = 0
        game.events = []
        game.game_phase = "ending"
        game.cat_dialogue = "...えへへ。ボクのこと、好きって言ってくれた♪ ありがとニャ！"
        game.add_event("🎉 和解成功！ハッピーエンド！")

        # 壁紙を設定 & BGM停止（バックグラウンド）
        def set_ending():
            # BGMをすべて停止
            run_script(PLAY_BGM, ["stop", "jealous"], async_mode=False)
            run_script(PLAY_BGM, ["stop", "healing"], async_mode=False)
            try:
                run_script(GENERATE_WALLPAPER, [RECONCILIATION_IMG], async_mode=False)
            except Exception:
                pass
            run_script(SET_WALLPAPER, [RECONCILIATION_IMG])

        threading.Thread(target=set_ending, daemon=True).start()
        return True, "和解成功！嫉妬猫が喜んでいます♪"
    else:
        game.cat_dialogue = "...それだけ？もっとちゃんと謝ってよ..."
        game.add_event("❌ 和解失敗...心が伝わらなかった")
        return False, "嫉妬猫はまだ怒っています...もっと優しい言葉をかけてあげて？"


# ══════════════════════════════════════════
# 嫉妬エスカレーションスレッド
# ══════════════════════════════════════════
def jealousy_tick_loop():
    """バックグラウンドで嫉妬レベルに応じたアクションを定期実行"""
    while True:
        time.sleep(4)
        if game.game_phase != "playing":
            continue

        level = game.jealousy_level
        if level <= 0:
            continue

        # たまにセリフを更新
        if random.random() < 0.4:
            game.update_dialogue()

        # たまにささやき声
        if level > 20 and random.random() < 0.25:
            run_script(WHISPER, [str(int(level))])

        # OS干渉トリガー
        trigger_os_action(level)


# ══════════════════════════════════════════
# HTTPサーバー
# ══════════════════════════════════════════
class GameHandler(SimpleHTTPRequestHandler):
    """ゲーム用HTTPリクエストハンドラ"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/state":
            self._json_response(game.to_dict())
        elif parsed.path.startswith("/api/"):
            self._json_response({"error": "Not found"}, 404)
        else:
            # 静的ファイルをサーブ
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        if parsed.path == "/api/start":
            game.game_phase = "playing"
            game.jealousy_level = 0
            game.pets_count = 0
            game.events = []
            game.cat_dialogue = "...ふぅん、始まったんだ。"
            game.add_event("🎬 ゲーム開始！")
            self._json_response({"status": "started"})

        elif parsed.path == "/api/pet":
            if game.game_phase == "playing":
                game.pets_count += 1
                # なでるほど嫉妬が上がる（5〜12のランダム上昇）
                increase = random.randint(5, 12)
                game.jealousy_level = min(game.jealousy_level + increase, 105)
                game.update_dialogue()

                stage, stage_name = game.get_stage()
                self._json_response({
                    "status": "ok",
                    "increase": increase,
                    "jealousy_level": game.jealousy_level,
                    "stage": stage,
                    "dialogue": game.cat_dialogue,
                })
            else:
                self._json_response({"status": "not_playing"})

        elif parsed.path == "/api/reconcile":
            text = data.get("text", "")
            if not text:
                self._json_response({"status": "error", "message": "テキストを入力してください"})
                return
            success, message = try_reconcile(text)
            self._json_response({
                "status": "success" if success else "failed",
                "message": message,
                "game_phase": game.game_phase,
            })

        elif parsed.path == "/api/restart":
            game.jealousy_level = 0
            game.pets_count = 0
            game.game_phase = "intro"
            game.events = []
            game.cat_dialogue = "..."
            self._json_response({"status": "restarted"})

        else:
            self._json_response({"error": "Not found"}, 404)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        # APIコールのログだけ出す
        if "/api/" in str(args[0]):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def main():
    PORT = 8888
    server = HTTPServer(("0.0.0.0", PORT), GameHandler)

    # 嫉妬ティックをバックグランドで起動
    tick_thread = threading.Thread(target=jealousy_tick_loop, daemon=True)
    tick_thread.start()

    print("=" * 50)
    print("  🐱 Jealousy.sys Game Server")
    print(f"  🌐 http://localhost:{PORT}")
    print("=" * 50)
    print("  Ctrl+C で停止")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        # BGMを停止
        run_script(PLAY_BGM, ["stop", "jealous"], async_mode=False)
        run_script(PLAY_BGM, ["stop", "healing"], async_mode=False)
        server.server_close()


if __name__ == "__main__":
    main()
