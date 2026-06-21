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
python build.py <テンプレートファイルのパス>
```

例:
```bash
python build.py template.md
python build.py templates/template_b.md
```

指定したテンプレートMDファイルのプレースホルダー（`{{TITLE}}` や `{{CODE}}` など）を置換して `output/` に Markdown ファイルを書き出します。

新しいテンプレートを追加する場合は、テンプレートファイルを作成し、実行時にそのパスを引数として指定するだけで利用できます。

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

## variantの追加方法

1. `snippets/`, `images/`, `tables/` のいずれかのフォルダに、
   同じ識別子（ファイル名）を持つファイルを配置する

   例：
   - `snippets/q2a.pseudo`
   - `images/q2a.png`
   - `tables/q2a.md`

   ファイル名（拡張子を除いた部分）が識別子になります。プレフィックスは不要です。

2. `python build.py <テンプレートファイル>` を実行すると、
   識別子が自動的に検出され、`output/q2a.md` が生成される

3. 画像やテーブルが用意できていないvariantがあっても処理は止まらず、
   コンソールに警告が表示されるだけで先に進む

## 同じ種類のプレースホルダーを複数使いたい場合

テンプレート側で番号付きのプレースホルダーを使用してください。

```markdown
{{IMAGE_1}}
{{IMAGE_2}}
```

対応するファイルも、同じ識別子＋番号の形式で配置します。

```
images/q1a_1.png
images/q1a_2.png
```

番号を付けない場合（1つだけの場合）は、従来通り番号なしのファイル名・プレースホルダーで構いません。

## フォルダとプレースホルダーの対応

| フォルダ | プレースホルダー | 処理内容 |
|---|---|---|
| `snippets/` | `{{CODE}}` | ファイル内容をそのまま差し込む |
| `images/` | `{{IMAGE}}` | `![図](パス)` というMarkdown画像記法に変換して差し込む |
| `tables/` | `{{TABLE}}` | ファイル内容をそのまま差し込む（Markdown表形式のファイルを想定） |

新しいフォルダ種別を追加する場合は、`build.py` の `FOLDER_TO_PLACEHOLDER` 辞書にエントリを追加するだけで対応できます。

### images/ フォルダについて

`images/` フォルダ内の `.png` ファイルはサンプルとしてダミーファイルが配置されています。
実際の画像に差し替えて使用してください。

## 前提条件

- Python 3.x
- Pandoc がインストール済みであること
- Eisvogel LaTeX テンプレート（`eisvogel.latex`）がインストール済みであること
