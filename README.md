# Markdown差し込み印刷システム

このシステムは、特定の文書形式に限定されない汎用的な差し込み印刷システムです。
テンプレートMDファイルに対して、コード・画像・表などの要素を差し込み、
複数バリエーションの文書（Markdown）を一括生成できます。
試験問題に限らず、どのような文書テンプレートにも応用可能です。

## ディレクトリ構成

```
project/
├── build.py          # ビルドスクリプト
├── template.md       # Markdown出力テンプレート（{{TITLE}}・{{CODE}} プレースホルダー）
├── titles.json       # スニペットファイル名 → 日本語タイトルの対応表
│
├── snippets/         # 差し込みコンテンツ（build.py の入力）
│   ├── 01_sample_a.pseudo
│   ├── 02_sample_b.pseudo
│   └── ...
│
├── output/           # build.py が生成する Markdown + Pandocで作るPDF
│   ├── 01_sample_a.md … （生成されたMarkdown）
│   ├── output_000.md （表紙・メタデータ）
│   ├── files.yml     （Pandoc用ファイルリスト → output.pdf）
│   └── output.pdf
│
└── question/         # サブプロジェクト用Markdown + Pandocで作るPDF
    ├── 01_sample.md … （生成されたMarkdown）
    ├── output_000.md （表紙・メタデータ）
    ├── files.yml     （Pandoc用ファイルリスト → document.pdf）
    └── document.pdf
```

## 使い方

### 1. Markdownを生成する

```bash
python build.py
```

`snippets/` にあるファイルを1つずつ読み込み、`template.md` のプレースホルダー（`{{TITLE}}` や `{{CODE}}` など）を置換して `output/` に Markdown ファイルを書き出します。

### 2. PDFに変換する

`output/` フォルダに移動し、Pandoc で PDF を生成します。

```bash
cd output
pandoc --defaults files.yml
```

`files.yml` に列挙された Markdown ファイルをまとめてPDFとして出力します。

別フォルダのPDFを生成する場合は `question/` フォルダで同様に実行してください。

```bash
cd question
pandoc --defaults files.yml
```

## スニペットを追加する手順

1. `snippets/` に新しいファイルを追加する（例: `06_sample_c.pseudo`）
2. `titles.json` に対応するタイトルを追加する

```json
{
  "sample_c": "サンプルコードC"
}
```

3. `python build.py` を実行して `output/` の Markdown を更新する
4. `output/files.yml` の `input-files` リストに `06_sample_c.md` を追加する
5. `pandoc --defaults output/files.yml` で PDF を再生成する

## variants の辞書構造（複数プレースホルダー対応）

`build.py` 内の `variants` 辞書は「variant名 → {プレースホルダー名: ファイルパス}」という構造になっています。

```python
variants = {
    "variant_a": {
        "CODE":  "snippets/q1_pattern_a.pseudo",
        "IMAGE": "images/q1_a_diagram.png",
        "TABLE": "tables/q1_a_trace.md",
    },
    "variant_b": {
        "CODE":  "snippets/q1_pattern_b.pseudo",
        "IMAGE": "images/q1_b_diagram.png",
        "TABLE": "tables/q1_b_trace.md",
    },
}
```

キー名（`CODE`, `IMAGE`, `TABLE` など）は `template.md` 内の `{{CODE}}`, `{{IMAGE}}`, `{{TABLE}}` と対応します。

### プレースホルダー種別ごとの処理

| プレースホルダー | 処理内容 |
|---|---|
| `CODE` | ファイル内容をそのまま差し込む（コードブロック内で使用） |
| `IMAGE` | `![図](パス)` というMarkdown画像記法に変換して差し込む |
| `TABLE` | ファイル内容をそのまま差し込む（Markdown表形式のファイルを想定） |
| その他 | ファイル内容をそのまま差し込む（デフォルト動作） |

### 新しいプレースホルダー種別を追加する手順

1. `template.md` に `{{新しいキー名}}` を追加する
2. 必要であれば `build.py` の `resolve_value()` 関数に変換処理を追加する
   （画像のように特殊な変換が必要な場合のみ。テキストそのまま差し込みなら不要）
3. `variants` 辞書の各エントリに新しいキーと対応ファイルパスを追加する

### images/ フォルダについて

`images/` フォルダ内の `.png` ファイルはサンプルとしてダミーファイルが配置されています。
実際の画像に差し替えて使用してください。

## 前提条件

- Python 3.x
- Pandoc がインストール済みであること
- Eisvogel LaTeX テンプレート（`eisvogel.latex`）がインストール済みであること
