# FE疑似言語問題集 ビルドシステム

FE（基本情報技術者試験）の疑似言語スタイルで書かれたコードスニペットをテンプレートに差し込み、MarkdownファイルとPDFを生成するシステムです。

## ディレクトリ構成

```
project/
├── build.py          # ビルドスクリプト
├── template.md       # Markdown出力テンプレート（{{TITLE}}・{{CODE}} プレースホルダー）
├── titles.json       # スニペットファイル名 → 日本語タイトルの対応表
│
├── snippets/         # 例題用疑似言語ソース（build.py の入力）
│   ├── 01_for.pseudo
│   ├── 02_while.pseudo
│   ├── 03_do_while.pseudo
│   ├── 04_array_1d.pseudo
│   └── 05_array_2d.pseudo
│
├── output/           # build.py が生成する Markdown + Pandocで作るPDF
│   ├── 01_for.md … 05_array_2d.md
│   ├── output_000.md （表紙・メタデータ）
│   ├── files.yml     （Pandoc用ファイルリスト → FE疑似言語例題.pdf）
│   └── FE疑似言語例題.pdf
│
├── 練習問題/          # 練習問題用疑似言語ソース（20問）
│   ├── 01_sum_1_to_n.pseudo … 20_matrix_transpose.pseudo
│   └── template.md
│
└── question/         # 練習問題のMarkdown + Pandocで作るPDF
    ├── 01_sum_1_to_n.md … 20_matrix_transpose.md
    ├── output_000.md （表紙・メタデータ）
    ├── files.yml     （Pandoc用ファイルリスト → FE疑似言語問題集.pdf）
    └── FE疑似言語問題集.pdf
```

## 使い方

### 1. Markdownを生成する

```bash
python build.py
```

`snippets/` にある `.pseudo` ファイルを1つずつ読み込み、`template.md` の `{{TITLE}}` と `{{CODE}}` を置換して `output/` に Markdown ファイルを書き出します。

### 2. PDFに変換する

`output/` フォルダに移動し、Pandoc で PDF を生成します。

```bash
cd output
pandoc --defaults files.yml
```

`files.yml` に列挙された Markdown ファイルをまとめて `FE疑似言語例題.pdf` として出力します。

練習問題PDFを生成する場合は `question/` フォルダで同様に実行してください。

```bash
cd question
pandoc --defaults files.yml
```

## スニペットを追加する手順

1. `snippets/` に新しいファイルを追加する（例: `06_if_else.pseudo`）
2. `titles.json` に対応するタイトルを追加する

```json
{
  "if_else": "条件分岐（if-else）"
}
```

3. `python build.py` を実行して `output/` の Markdown を更新する
4. `output/files.yml` の `input-files` リストに `06_if_else.md` を追加する
5. `pandoc --defaults output/files.yml` で PDF を再生成する

## 練習問題一覧（question/）

| No. | ファイル名 | タイトル |
|-----|-----------|---------|
| 01 | sum_1_to_n | 1からnの合計 |
| 02 | factorial | 階乗 |
| 03 | array_sum | 配列の合計 |
| 04 | array_max | 配列の最大値 |
| 05 | array_min | 配列の最小値 |
| 06 | array_average | 配列の平均 |
| 07 | even_numbers | 偶数の列挙 |
| 08 | array_reverse_print | 配列の逆順出力 |
| 09 | linear_search | 線形探索 |
| 10 | bubble_sort | バブルソート |
| 11 | selection_sort | 選択ソート |
| 12 | fizzbuzz | FizzBuzz |
| 13 | prime_numbers | 素数の列挙 |
| 14 | matrix_row_sum | 行列の行合計 |
| 15 | matrix_col_sum | 行列の列合計 |
| 16 | matrix_diagonal_sum | 行列の対角和 |
| 17 | fibonacci | フィボナッチ数列 |
| 18 | gcd_euclidean | ユークリッドの互除法 |
| 19 | count_occurrences | 出現回数の集計 |
| 20 | matrix_transpose | 行列の転置 |

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
