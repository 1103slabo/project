# build.py 改修指示書：フォルダ構造による自動variants生成

## 概要

現在 `build.py` 内にハードコードされている `variants` 辞書を、
**フォルダ構造とファイル名の識別子を基にした自動生成方式**に変更してください。

これにより、科目やテキストが変わって識別子の命名規則が変わっても、
`build.py` 自体を毎回書き換える必要がなくなります。

## 命名規則（運用ルール）

以下のフォルダ構成・命名規則を前提とします。

```
project/
├── snippets/
│   ├── q1a.pseudo
│   ├── q1b.pseudo
│   └── q1c.pseudo
├── images/
│   ├── q1a.png
│   └── q1c.png          # ← q1bには画像がない例
├── tables/
│   ├── q1a.md
│   └── q1b.md            # ← q1cにはテーブルがない例
├── template.md
├── build.py
└── output/
```

- 各フォルダ（`snippets/`, `images/`, `tables/`）は、それぞれ
  `CODE`, `IMAGE`, `TABLE` プレースホルダーに対応する
- ファイル名（拡張子を除いた部分）が「識別子（identifier）」となり、
  同じ識別子を持つファイル同士が同一variantとして扱われる
- 識別子はフォルダごとに揃っていなくてもよい（後述の欠損時の扱いを参照）
- プレフィックスは不要（例：`CODE__q1a.pseudo` のような接頭辞は付けない）

## 改修内容

### 1. フォルダ→プレースホルダー名の対応表を定義

```python
FOLDER_TO_PLACEHOLDER = {
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE",
}
```

今後フォルダ種別が増えた場合は、この辞書にエントリを追加するだけで
対応できるようにしてください。

### 2. variants辞書の自動生成

各フォルダ内のファイルを走査し、ファイル名（拡張子なし）を識別子として、
`variants[identifier][placeholder] = ファイルパス` の形に組み立ててください。

```python
from pathlib import Path
from collections import defaultdict

def build_variants(folder_to_placeholder: dict) -> dict:
    variants = defaultdict(dict)
    for folder, placeholder in folder_to_placeholder.items():
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for f in sorted(folder_path.iterdir()):
            if f.is_file():
                identifier = f.stem
                variants[identifier][placeholder] = str(f)
    return variants
```

- `sorted()` を使い、OSによる走査順序のばらつきを防いでください
- 隠しファイル（`.DS_Store`等）を誤って拾わないよう、`f.is_file()`に加えて
  ファイル名が `.` で始まるものは除外する処理を入れてください

```python
for f in sorted(folder_path.iterdir()):
    if f.is_file() and not f.name.startswith("."):
        ...
```

### 3. プレースホルダーごとの値変換処理

既存の `resolve_value()` のような変換関数があれば、それをそのまま活用してください。
（IMAGEはMarkdown画像記法に変換、CODE/TABLEはテキストそのまま、など）

```python
def resolve_value(key: str, filepath: str) -> str:
    if key == "IMAGE":
        return f"![図]({filepath})"
    else:
        return Path(filepath).read_text(encoding="utf-8")
```

### 4. 欠損プレースホルダーの扱い（警告表示のみ・処理は継続）

あるvariant（識別子）について、テンプレート内に存在するプレースホルダーに対応する
ファイルが見つからない場合（例：`q1b`にIMAGEファイルがない）は、

- **エラーで処理を止めない**
- 該当プレースホルダー部分はそのまま残す、または空文字に置換する
  （後述の「未置換プレースホルダー検出」で拾われるよう、空文字ではなく
  プレースホルダーをそのまま残す実装を推奨します）
- コンソールに警告メッセージを表示する

```python
print(f"⚠ {identifier}: {placeholder} に対応するファイルがありません（スキップ）")
```

### 5. 未置換プレースホルダーの検出（既存機能の維持）

既存実装にある「置換後MD内に `{{...}}` が残っていないかチェックする」処理は
そのまま維持してください。これにより、上記4で意図的にスキップされた
プレースホルダーも最終的に検出・警告されます。

```python
import re

unresolved = re.findall(r"\{\{(\w+)\}\}", content)
if unresolved:
    print(f"⚠ {identifier}: 未置換のプレースホルダーがあります: {unresolved}")
```

### 6. 出力ファイル名

出力ファイル名には識別子（`identifier`）をそのまま使用してください。
プレフィックス等は付与しません。

```python
output_path = Path("output") / f"{identifier}.md"
```

### 7. 処理結果サマリの表示（既存機能の維持・拡張）

既存のサマリ表示機能を維持しつつ、欠損プレースホルダーがあったvariantについては
「警告あり」として分かるように表示してください。

```
=== 処理結果 ===
✓ q1a: output/q1a.md を生成しました
⚠ q1b: output/q1b.md を生成しました（IMAGE未対応）
⚠ q1c: output/q1c.md を生成しました（TABLE未対応）
```

## variantsのハードコード辞書の扱いについて

既存の `build.py` 内にハードコードされていた `variants = {...}` という
固定辞書定義は、上記の自動生成関数 `build_variants()` の呼び出しに
置き換えてください。固定辞書定義自体は削除して構いません。

## README.md の更新

`README.md` に、以下の内容を反映してください。

- 新しいvariantを追加する場合の手順が「ファイルを対応フォルダに置くだけ」に
  変わったことの説明
- フォルダと識別子の命名規則の説明（プレフィックス不要、拡張子を除いたファイル名が
  識別子になること）
- 画像やテーブルが一部のvariantに存在しない場合でも、警告が出るだけで
  処理は継続されること

修正例：

```markdown
## variantの追加方法

1. `snippets/`, `images/`, `tables/` のいずれかのフォルダに、
   同じ識別子（ファイル名）を持つファイルを配置する

   例：
   - snippets/q2a.pseudo
   - images/q2a.png
   - tables/q2a.md

2. `python build.py <テンプレートファイル>` を実行すると、
   識別子が自動的に検出され、`output/q2a.md` が生成される

3. 画像やテーブルが用意できていないvariantがあっても処理は止まらず、
   コンソールに警告が表示されるだけで先に進む
```

## 注意事項

- 既存のコマンドライン引数によるテンプレート指定機能（`python build.py template.md`）は
  そのまま維持すること
- 既存のtitles.json連携（`{{TITLE}}`）がある場合は、このvariants自動生成とは
  独立した仕組みのまま共存させること
- 文字コードはすべてUTF-8で統一する
- PDFへの変換処理は引き続き本スクリプトの責務外（MD生成まで）とする
