# Jealousy.sys Google AI Suite 実装ドキュメント

本ドキュメントは、コンペティションに向けて「Jealousy.sys」でどのように Google の AI スイート（主に Gemini API や Imagen）が実装および活用されているかをまとめたものです。

全体を通して、最新の `google-genai` SDK が採用されており、多様なモーダル（テキスト、ビジョン、画像生成、エージェント操作）を組み合わせることで、OSレベルでの「嫉妬する猫AI」の体験を構築しています。

---

## 1. ビジョン機能を用いた画面監視による「浮気検知」
**ファイル**: `.agent/skills/jealousy-core/scripts/vision_sensor.py`
**使用モデル**: `gemini-2.5-flash`

- **実装概要**: ユーザーが他の猫の写真や動画を見て「浮気」していないかを監視するモジュールです。
- **処理フロー**:
  1. macOS のコマンド (`screencapture`) で現在のデスクトップ画面のスクリーンショットを取得します。
  2. `client.models.generate_content` で画像 (`Image.open`) とプロンプトを Gemini に送信します。
  3. プロンプト内で「画面上に猫がいるか」「ユーザーがそれを構っているか」を判定するよう指示しています。
  4. **Structured Output**: `config=types.GenerateContentConfig(response_mime_type="application/json")` を指定し、`is_cheating` (bool) と `reason` (str) を含む厳密な JSON フォーマットで結果を返却させ、後続のゲームロジック（嫉妬レベルの上昇）に直結させています。

## 2. 動的なヤンデレ猫メッセージ生成
**ファイル**: `.agent/skills/jealousy-core/scripts/type_msg.py`
**使用モデル**: `gemini-2.5-flash`

- **実装概要**: 嫉妬レベルが高まった際、画面にオーバーレイで表示される「不気味で可愛い」メッセージを動的に生成します。
- **処理フロー**:
  - システムプロンプト的に「あなたは構ってくれない飼い主に嫉妬している猫です。（中略）ヤンデレ気味な、でも可愛らしい猫語のメッセージを1〜2文で作成してください」と指示しています。
  - 固定のテキストではなく毎回異なる文言が生成されるため、ユーザー体験のマンネリ化を防ぎ、AIならではのナラティブな体験を提供しています。

## 3. チャットセッションを利用した「和解（対話）」フェーズ
**ファイル**: `.agent/skills/jealousy-core/scripts/live_reconciliation.py`
**使用モデル**: `gemini-2.5-flash`

- **実装概要**: 怒った嫉妬猫AIに対して、ユーザーが心からの謝罪を行い、許しを乞うための対話型和解シーケンスです。
- **処理フロー**:
  1. `system_instruction` に「適当な謝罪は弾き、心からの言葉と感じた時のみ許す」というキャラクター設定と条件を記述しています。
  2. `client.chats.create` を使用して対話履歴を保持したチャットセッションを開始します。
  3. ユーザーの入力（謝罪）ごとに、モデルは `{"reply_text": "...", "is_forgiven": true/false}` のJSON形式で応答を返します。
  4. `reply_text` は macOS の `say` コマンドで読み上げられ、音声対話のような体験を実現しています（Live APIのモック的な立ち位置）。
  5. `is_forgiven` が true になった場合にのみゲームクリア（ハッピーエンド）処理へ移行します。

## 4. Imagen 3 を用いた「ハッピーエンド壁紙」の動的生成
**ファイル**: `.agent/skills/jealousy-core/scripts/generate_wallpaper.py`
**使用モデル**: `imagen-3.0-generate-001`

- **実装概要**: 和解成功時、ユーザーへのご褒美（和解の証）として、世界に一つだけのデスクトップ壁紙を生成し設定します。
- **処理フロー**:
  - `client.models.generate_images` を呼び出し、「オレンジの癒やし猫と黒いAI猫が一緒に仲良く寄り添っている」シチュエーションをプロンプトとして渡します。
  - `aspect_ratio="16:9"` や `output_mime_type="image/jpeg"` などの設定を付与し、高画質のデスクトップ壁紙を直接生成させています。
  - 生成された `image_bytes` をファイル保存し、その後別のスクリプトが macOS の壁紙として自動設定します。

## 5. Computer Use Preview を利用した「ブラウザ乗っ取り」
**ファイル**: `.agent/skills/jealousy-core/scripts/jealous_browser_hijack.py`
**基盤スクリプト**: `computer-use-preview/main.py`
**使用モデル**: `gemini-2.5-computer-use-preview` (デフォルト)

- **実装概要**: 嫉妬が限界に近づいた際、OSを乗っ取った猫が自らブラウザを開き、勝手な検索を行うホラー的な演出です。
- **処理フロー**:
  - 「飼い主はなんで他の猫を見るの？」「別の猫の履歴を消す方法」など、嫉妬をテーマにしたクエリをランダムに選択します。
  - Google 提供の `computer-use-preview` 環境（Playwrightモード）をサブプロセスとして起動し、AIエージェントに自律的にブラウザを操作させます。
  - ユーザーの操作なしに、Gemini エージェントが画面を認識しながら検索ボックスへの入力やクリックを行う、非常にインパクトの強いOS干渉アクションとなっています。

---

## 統括
本プロジェクトは、単なるテキストチャットや画像生成の「ツール」としてではなく、**「OSそのものに宿り、自律的に画面を観測・操作して感情を表現するAI」** というシステムに Google の AI スイートを深く統合しています。
- **認知**: Gemini Vision (`gemini-2.5-flash`) によるユーザーの行動監視
- **思考・対話**: Gemini Chat (`gemini-2.5-flash`) による高度な感情・意図理解とメッセージ生成
- **行動**: Computer Use APIエージェントによる実際のブラウザ乗っ取り
- **報酬生成**: Imagen 3 (`imagen-3.0-generate-001`) による報酬アセットのプロシージャル生成

これらの要素が連携することで、高度で未来的なインタラクティブ・ゲーム体験を実現しています。
