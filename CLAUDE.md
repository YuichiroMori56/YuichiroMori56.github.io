# yuichiro-profile

森 雄一郎（Yuichiro Mori）の研究者プロフィール・業績管理リポジトリ。
GitHub Pages でパーソナルウェブサイトとして公開する（https://yuichiromori56.github.io/）。

## リポジトリ構成

```
profile/
├── CLAUDE.md              ← 本ファイル
├── cv.md                  ← ★ Single Source of Truth（CV・業績・研究費）
├── cv.css                 ← CV 表示用スタイル（cv.html / cv.pdf にも使用）
├── build/
│   ├── build.py           ← cv.md → ウェブサイトの自動ビルド（CI で実行）
│   └── pdf.css            ← cv.pdf 生成用の追加スタイル
├── .github/workflows/
│   └── deploy.yml         ← push 時に自動ビルド & GitHub Pages デプロイ
└── website/               ← サイトの静的部分（テンプレート）
    ├── index.html         ← 英語版（About/Research/Contact は手書き、一覧は自動生成）
    ├── ja.html            ← 日本語版（同上）
    ├── css/style.css
    └── assets/            ← profile.jpg, favicon.svg
```

## 仕組み（重要）

**cv.md が唯一のマスターデータ。** push すると GitHub Actions が以下を自動実行する：

1. `build/build.py` が cv.md を解析し、以下を index.html / ja.html のマーカー間に注入
   - Peer-reviewed publications（筆頭/責任著者と共著に自動分類、年バッジ付き）
   - Awards and Honors
   - Invited Talks
2. pandoc で cv.md → `cv.html`（フル CV ページ）を生成
3. weasyprint で `assets/cv.pdf` を生成
4. `_site/` を GitHub Pages にデプロイ

つまり **論文・受賞・講演の追加は cv.md を1箇所編集して push するだけ**。
HTML は編集不要（website/*.html のマーカー間の内容はプレースホルダで、デプロイ時に上書きされる）。

### cv.md 内で使えるアノテーション（HTML コメントなので PDF には出ない）

- `<!-- ja: 日本語訳 -->` … ja.html でこの日本語を表示（受賞名など）
- `<!-- web:hide -->` … その項目をウェブサイトに載せない（CV/PDF には残る）

### ビルドマーカー（website/index.html, ja.html 内）

`<!-- BUILD:pubs-first -->`〜`<!-- /BUILD:pubs-first -->`, `pubs-co`, `awards`, `talks`。
マーカーを消さないこと。

## 更新フロー

1. cv.md を編集（新しい論文・受賞・講演を追加）
2. commit & push（branch: `master`）
3. GitHub Actions が自動でビルド & デプロイ（Actions タブで確認可能）

About 文・研究テーマ・連絡先など静的な部分を変える場合のみ website/*.html を直接編集する。

## cv.md の書式ルール（ビルドが依存）

- セクション見出しは `## PEER-REVIEWED PUBLICATIONS` / `## AWARDS AND HONORS` / `## INVITED TALKS`（変更しない）
- 論文は `1. Mori Y, ... Title. *Journal.* Year;...` 形式の番号付きリスト、1項目1行
- 筆頭/責任著者の判定は「Mori Y」で始まるかどうか
- 年バッジは引用文中の最後の4桁西暦から抽出（年がなければバッジ省略）
- 受賞・講演は2列テーブル `| 年 | 内容 |`

## ローカル環境の注意

- このマシンには実 Python がない（Store スタブのみ）ため、ビルドは CI 上でのみ実行する。
  ローカル検証が必要な場合は pandoc（インストール済み）で cv.md のレンダリング確認は可能。
- デザインはシンプル・アカデミックなトーン。vanilla HTML/CSS/JS、外部フレームワーク不要。
- 画像は website/assets/ に配置。
