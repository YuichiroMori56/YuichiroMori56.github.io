# yuichiro-profile

森 祐一朗（Yuichiro Mori）の研究者プロフィール・業績管理リポジトリ。
GitHub Pages でパーソナルウェブサイトとして公開する。

## リポジトリ構成

```
profile/
├── CLAUDE.md          ← 本ファイル
├── cv.md              ← CV・業績・研究費を一括管理
├── .gitignore
└── website/           ← GitHub Pages デプロイ対象
    ├── index.html
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── assets/
```

## 方針

- **cv.md** がマスターデータ。CV・Publications・Grants を1ファイルで管理し、website/ 側から参照して HTML を生成する。
- **website/** ディレクトリを GitHub Pages の公開ルートとする（リポジトリ設定: Source → `main` branch, `/website` folder）。
- デザインはシンプル・アカデミックなトーン。レスポンシブ対応。
- 外部フレームワーク不要。vanilla HTML/CSS/JS で構成する。

## 業績データの書式（cv.md 内）

```markdown
## Publications
### Peer-reviewed Articles
1. **Mori Y**, Author B, Author C. Title. *Journal Name*. Year;Volume(Issue):Pages. doi:XXX

### Conference Presentations
1. **Mori Y**. Title. Conference Name, City, Date. (Oral/Poster)

## Grants & Funding
### Principal Investigator
1. Title of Grant. Funding Agency. Period. Amount.

### Co-Investigator
1. Title of Grant (PI: Name). Funding Agency. Period. Amount.
```

## ウェブサイト更新フロー

1. cv.md を編集
2. website/ 内の HTML を更新（将来的にビルドスクリプトで自動化可能）
3. commit & push → GitHub Pages が自動デプロイ

## コーディング規約

- HTML/CSS/JS はフォーマッタ不要。読みやすさ優先。
- 日本語・英語バイリンガル対応を想定。
- 画像は website/assets/ に配置。
