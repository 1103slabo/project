# build.py 汎用化（複数プレースホルダー対応）改修指示書

## 概要

現在の `build.py` は `{{CODE}}` という1種類のプレースホルダーのみを
スニペットファイルの内容で置換し、Markdownファイルを生成する仕組みになっています。

これを、**任意の数のプレースホルダー（CODE, IMAGE, TABLE など）に対応できる
汎用的な構造**に改修してください。

PDFへの変換はこのスクリプトの責務ではありません。
（既存方針通り、build.pyの出力は `output/` フォルダ内のMDファイルまでとします）

## 改修内容

### 1. variants の構造変更

現状の「variant名 → 1つのファイルパス（文字列）」という構造から、
「variant名 → {プレースホルダー名: ファイルパス} の辞書」という構造に変更してください。

```python
variants = {
    "variant_a": {
        "CODE": "snippets/q1_pattern_a.pseudo",
        "IMAGE": "images/q1_a_diagram.png",
        "TABLE": "tables/q1_a_trace.md",
    },
    "variant_b": {
        "CODE": "snippets/q1_pattern_b.pseudo",
        "IMAGE": "images/q1_b_diagram.png",
        "TABLE": "tables/q1_b_trace.md",
    },
}
```

- キー名（`CODE`, `IMAGE`, `TABLE` など）は、テンプレートMD内のプレースホルダー名
  `{{CODE}}`, `{{IMAGE}}`, `{{TABLE}}` と一致させること。
- 既存の `titles.json` によるタイトル置換ロジック（`{{TITLE}}`）がある場合は、
  そのまま活かしつつ、このvariants辞書方式と共存できる形にしてください。

### 2. 置換処理のループ化

プレースホルダーごとに個別の `.replace()` を書くのではなく、
`variants[name]` の中身をループして汎用的に処理してください。

```python
content = template
for key, filepath in parts.items():
    value = Path(filepath).read_text(encoding="utf-8")
    content = content.replace(f"{{{{{key}}}}}", value)
```

### 3. ファイル種別ごとの変換処理（重要）

プレースホルダーの種類によって、ファイルの中身をそのまま差し込むのか、
Markdown記法に変換してから差し込むのかが異なります。
**プレースホルダー名（キー）に応じて処理を分岐**させてください。

| プレースホルダー名 | 処理内容 |
|---|---|
| `CODE` | ファイル内容をそのままテキストとして差し込む（コードブロック内で使われる前提） |
| `IMAGE` | ファイルパスを `![図](パス)` というMarkdown画像記法に変換してから差し込む |
| `TABLE` | ファイル内容をそのままテキストとして差し込む（Markdown表形式のファイルを想定） |
| 上記以外の未知のキー | ひとまずテキストとしてそのまま差し込む（デフォルト動作） |

実装イメージ：

```python
def resolve_value(key: str, filepath: str) -> str:
    if key == "IMAGE":
        return f"![図]({filepath})"
    else:
        return Path(filepath).read_text(encoding="utf-8")
```

このような変換関数を用意し、ループ内で `key` ごとに呼び出す形にしてください。
今後プレースホルダー種別が増えることを想定し、分岐は辞書（マッピングテーブル）か
if/elif で見通し良く書いてください。

### 4. 未置換プレースホルダーの検出（警告表示）

置換後のMD内に `{{...}}` の形式が残っていないかを正規表現でチェックし、
残っている場合はコンソールに警告を表示してください（処理は継続）。

```python
import re

unresolved = re.findall(r"\{\{(\w+)\}\}", content)
if unresolved:
    print(f"⚠ {name}: 未置換のプレースホルダーがあります: {unresolved}")
```

- これは「variantsの辞書に対応するキーを書き忘れた」場合の検出に使います。
- 警告が出ても処理自体は止めず、次のvariantの処理に進んでください。

### 5. 存在しないファイルパスへのエラーハンドリング

`variants` 内で指定されたファイルパスが実際には存在しない場合、
`Path.read_text()` が例外を出して止まってしまうため、
try/exceptで捕捉し、エラー内容を表示した上で
**そのvariantの処理だけスキップして次に進む**ようにしてください。

```python
try:
    value = Path(filepath).read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"✗ {name}: ファイルが見つかりません: {filepath}")
    continue  # このvariant全体をスキップする想定であれば外側ループでcontinue
```

### 6. 処理結果のサマリ表示

全variant処理後、以下のような簡易サマリをコンソールに表示してください。

```
=== 処理結果 ===
✓ variant_a: output/variant_a.md を生成しました
✓ variant_b: output/variant_b.md を生成しました
✗ variant_c: スキップ（ファイル未検出: snippets/q1_pattern_c.pseudo）
```

## 動作確認用のサンプルファイル追加

改修後の動作確認のため、以下のサンプルファイルも追加で作成してください。

- `images/` フォルダを作成し、サンプル画像ファイルを1つ配置（ダミーでよい。
  実画像が用意できない場合は、空のプレースホルダーファイルでもよいので
  その旨をREADMEに明記してください）
- `tables/` フォルダを作成し、サンプルのMarkdown表ファイルを1つ作成
  （例: `tables/q1_a_trace.md` にトレース表のMarkdown表を記述）
- `template.md` に `{{IMAGE}}` と `{{TABLE}}` のプレースホルダーを追加した
  サンプルセクションを追記（既存の `{{CODE}}` 部分は維持）

## README.md の更新

既存の `README.md` に、以下を追記してください。

- variantsの辞書構造の説明（プレースホルダー名をキーにすること）
- 新しいプレースホルダー種別を追加する場合の手順
  1. `template.md` に `{{新しいキー名}}` を追加
  2. 必要であれば `resolve_value()` 内に変換処理を追加（画像のような特殊な型の場合のみ）
  3. `variants` 辞書の各エントリに新しいキーと対応ファイルパスを追加

## 注意事項

- PDFへの変換処理は引き続き含めない（MD生成までがこのスクリプトの責務）
- 既存の `titles.json` を使った `{{TITLE}}` 置換ロジックがすでに実装されている場合は、
  それを壊さないように統合すること（壊れる場合は統合方法を提案してから実装してよい）
- 文字コードはすべてUTF-8で統一する
- 既存のファイル命名規則（アンダースコア区切り、小文字英語）を踏襲する
