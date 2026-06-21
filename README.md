# Markdown差し込み印刷システム

このシステムは、特定の文書形式に限定されない汎用的な差し込み印刷システムです。
テンプレートMDファイルに対して、コード・画像・表などの要素を差し込み、
複数バリエーションの文書（Markdown）を一括生成できます。
試験問題に限らず、どのような文書テンプレートにも応用可能です。

## ディレクトリ構成

```
project/
├── build.py              # ビルドスクリプト
├── template.md           # Markdown出力テンプレート（問題用）
├── template-answer.md    # Markdown出力テンプレート（解答用）
├── titles.json           # 識別子 → 日本語タイトルの対応表
│
├── snippets/             # コード差し込みコンテンツ（{{CODE}} に対応）
│   └── q1_a.pseudo
│
├── images/               # 画像差し込みコンテンツ（{{IMAGE}} に対応）
│   ├── q1_a_1.png
│   └── q1_a_2.png
│
├── tables/               # 表差し込みコンテンツ（{{TABLE}} に対応）
│   └── q1_a.md
│
├── output/               # build.py が生成する Markdown（Pandoc でPDF化）
│   └── q1_a.md
│
└── Instructions/         # このシステムの構築・変更指示書（参考資料）

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

## フォルダとプレースホルダーの対応設定

`folder_mapping.json` で、どのフォルダがどのプレースホルダーに対応するかを管理しています。

```json
{
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE"
}
```

| フォルダ | プレースホルダー | 処理内容 |
|---|---|---|
| `snippets/` | `{{CODE}}` | ファイル内容をそのまま差し込む |
| `images/` | `{{IMAGE}}` | `![図](パス)` というMarkdown画像記法に変換して差し込む |
| `tables/` | `{{TABLE}}` | ファイル内容をそのまま差し込む（Markdown表形式のファイルを想定） |

新しい種類のファイル（例: 音声、グラフ等）を追加したい場合は、対応するフォルダを作成し、`folder_mapping.json` にエントリを追加するだけで使えるようになります。`build.py` を編集する必要はありません。

```json
{
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE",
    "graphs": "GRAPH"
}
```

設定ファイルのパスを変更したい場合は、`--mapping` オプションで指定できます。

```bash
python build.py template.md --mapping mapping_kanji.json
```

### images/ フォルダについて

`images/` フォルダ内の `.png` ファイルはサンプルとしてダミーファイルが配置されています。
実際の画像に差し替えて使用してください。

## 前提条件

- Python 3.x
- Pandoc がインストール済みであること
- Eisvogel LaTeX テンプレート（`eisvogel.latex`）がインストール済みであること
