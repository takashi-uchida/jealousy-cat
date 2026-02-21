#!/usr/bin/swift
// chaotic_mouse.swift
// マウスを小刻みに震わせてイライラを表現するスクリプト (macOS標準搭載のSwiftを使用)

import Foundation
import CoreGraphics

print("🐭 マウスを小刻みに搖らします（嫉妬・イライラ表現）...")

// 現在のマウス位置を取得
guard let event = CGEvent(source: nil) else { 
    print("イベントソースを取得できませんでした")
    exit(1) 
}
var currentLoc = event.location

// 小刻みにガクガク震えるような動き（50回）
for _ in 1...50 {
    let dx = CGFloat.random(in: -20...20)
    let dy = CGFloat.random(in: -20...20)
    let newLoc = CGPoint(x: currentLoc.x + dx, y: currentLoc.y + dy)
    
    let moveEvent = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: newLoc, mouseButton: .left)
    moveEvent?.post(tap: .cghidEventTap)
    
    currentLoc = newLoc
    Thread.sleep(forTimeInterval: 0.03)
}
