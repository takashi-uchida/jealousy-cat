#!/usr/bin/swift
// cat_pounce.swift
// 猫がマウスカーソルに飛びかかるような動きを再現するスクリプト

import Foundation
import CoreGraphics

print("🐾 猫がマウスカーソルを捕まえようとしています...")

// 現在のマウス位置を取得
guard let event = CGEvent(source: nil) else { 
    print("イベントを取得できませんでした")
    exit(1) 
}
let startLoc = event.location

// 1. 「ため」の動作（ガタガタ震える）
for _ in 1...10 {
    let jitterX = CGFloat.random(in: -3...3)
    let jitterY = CGFloat.random(in: -3...3)
    let jitterLoc = CGPoint(x: startLoc.x + jitterX, y: startLoc.y + jitterY)
    
    let moveEvent = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: jitterLoc, mouseButton: .left)
    moveEvent?.post(tap: .cghidEventTap)
    Thread.sleep(forTimeInterval: 0.05)
}

// 2. 「飛びかかり」（一気に移動 + クリック（ドラッグ））
let targetX = startLoc.x + CGFloat.random(in: -200...200)
let targetY = startLoc.y + CGFloat.random(in: -200...200)
let targetLoc = CGPoint(x: targetX, y: targetY)

// 左マウスダウン
let mouseDownEvent = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: startLoc, mouseButton: .left)
mouseDownEvent?.post(tap: .cghidEventTap)

// 素早く移動（ドラッグ）
let steps = 10
for i in 1...steps {
    let progress = CGFloat(i) / CGFloat(steps)
    let currentX = startLoc.x + (targetLoc.x - startLoc.x) * progress
    let currentY = startLoc.y + (targetLoc.y - startLoc.y) * progress
    let dragLoc = CGPoint(x: currentX, y: currentY)
    
    let dragEvent = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDragged, mouseCursorPosition: dragLoc, mouseButton: .left)
    dragEvent?.post(tap: .cghidEventTap)
    Thread.sleep(forTimeInterval: 0.01)
}

// 左マウスアップ
let mouseUpEvent = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: targetLoc, mouseButton: .left)
mouseUpEvent?.post(tap: .cghidEventTap)

print("✨ ガシッ！捕まえた！")
