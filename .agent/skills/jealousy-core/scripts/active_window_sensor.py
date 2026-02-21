#!/usr/bin/env python3
# active_window_sensor.py
# macOSの最前面のウィンドウタイトルを取得するセンサースクリプト
# PyObjCを使用して現在のアプリケーション情報を取得します

import time

try:
    from AppKit import NSWorkspace
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
except ImportError:
    print("Error: PyObjC is required. Please install it using 'pip install pyobjc'")
    exit(1)

def get_active_window_title():
    # 最前面のアプリケーションを取得
    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
    if not active_app:
        return "Unknown"
        
    app_name = active_app.localizedName()
    
    # さらに詳細なウィンドウタイトルを取得（画面収録権限が必要）
    window_title = ""
    try:
        options = kCGWindowListOptionOnScreenOnly
        window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
        
        for window in window_list:
            # windowOwnerName がアクティブなアプリ名と一致し、kCGWindowLayer が 0 (標準ウィンドウ) のものを探す
            if window.get('kCGWindowOwnerName') == app_name and window.get('kCGWindowLayer') == 0:
                title = window.get('kCGWindowName', '')
                if title:
                    window_title = title
                    break
    except Exception:
        pass # 権限がない場合はアプリ名のみ返す

    if window_title:
        return f"{app_name} - {window_title}"
    return app_name

if __name__ == "__main__":
    current = get_active_window_title()
    print(current)
