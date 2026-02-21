#!/usr/bin/env python3
# reconcile_dialog.py
# 和解用のネイティブダイアログ
# macOS のネイティブダイアログを使ってユーザーに入力を求める

import subprocess
import sys
import os

# 和解成功の判定キーワード
RECONCILE_KEYWORDS = [
    "好き", "大好き", "ごめん", "ごめんね", "すき", "一番",
    "かわいい", "可愛い", "大切", "愛してる", "許して",
    "ごめんなさい", "仲直り", "love", "sorry",
    "なでなで", "よしよし", "いい子", "構ってあげる",
]


def show_native_dialog(title, message, default_answer=""):
    """macOSネイティブの入力ダイアログを表示"""
    script = f'''
    set dialogResult to display dialog "{message}" with title "{title}" default answer "{default_answer}" buttons {{"送信", "キャンセル"}} default button "送信" with icon caution
    if button returned of dialogResult is "送信" then
        return text returned of dialogResult
    else
        return ""
    end if
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        print(f"❌ Dialog error: {e}")
        return ""


def show_alert(title, message, icon="note"):
    """macOSネイティブのアラートを表示"""
    icon_map = {
        "note": "note",
        "caution": "caution",
        "stop": "stop",
    }
    icon_name = icon_map.get(icon, "note")
    script = f'''
    display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" with icon {icon_name}
    '''
    try:
        subprocess.run(["osascript", "-e", script], timeout=30)
    except Exception:
        pass


def show_reconcile_sequence():
    """
    和解シーケンスを実行。
    ネイティブダイアログでユーザーに入力を求め、キーワード判定する。
    戻り値: (success: bool, user_text: str)
    """
    # まず警告ダイアログ
    show_alert(
        "🐈‍⬛ Jealousy.sys — 限界突破",
        "嫉妬猫の怒りが限界に達しました！\\n\\n"
        "このままでは大変なことになります...\\n"
        "優しい言葉をかけて猫をなだめてください。"
    )

    # 入力ダイアログ
    max_attempts = 3
    for attempt in range(max_attempts):
        remaining = max_attempts - attempt
        text = show_native_dialog(
            "🐈‍⬛ 嫉妬猫に話しかける",
            f"嫉妬猫をなだめる言葉を入力してください（残り{remaining}回）\\n\\n"
            f"💡 ヒント: 猫の好きなこと、褒める言葉、謝罪など...",
            default_answer=""
        )

        if not text:
            # キャンセルされた
            continue

        # キーワード判定
        score = sum(1 for kw in RECONCILE_KEYWORDS if kw in text.lower())

        if score >= 1:
            show_alert(
                "🎉 和解成功！",
                f"嫉妬猫: 「...えへへ。{text}って言ってくれたの？\\n"
                f"ありがとニャ！もう怒ってないよ♪」",
                icon="note"
            )
            return True, text
        else:
            if remaining > 1:
                show_alert(
                    "❌ 和解失敗...",
                    f"嫉妬猫: 「...それだけ？もっとちゃんと言ってよ...」\\n\\n"
                    f"もう一度チャンスがあります。",
                    icon="caution"
                )
            else:
                show_alert(
                    "💔 最後のチャンスを逃しました...",
                    "嫉妬猫: 「...もういいよ。...でも本当は許してほしかった...」\\n\\n"
                    "ゲームを再スタートします。",
                    icon="stop"
                )

    return False, ""


if __name__ == "__main__":
    success, text = show_reconcile_sequence()
    if success:
        print(f"✅ 和解成功！ユーザーの言葉: {text}")
        sys.exit(0)
    else:
        print("❌ 和解失敗")
        sys.exit(1)
