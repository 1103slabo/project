# build.py 改修指示書：プレースホルダーの連番対応（全種別共通）

## 概要

現在のフォルダベース自動variants生成（`CODE`, `IMAGE`, `TABLE`等）に対し、
**同じ種類のプレースホルダーがテンプレート内に複数回登場するケース**に
対応できるよう改修してください。

例：

```markdown
## 図

{{IMAGE_1}}

{{IMAGE_2}}
```

この機能は `IMAGE` に限らず、`CODE`, `TABLE`、および今後追加されうる
すべてのプレースホルダー種別に対して**共通の仕組み**で対応できるようにしてください。

## 命名規則（運用ルール）

### テンプレート側

連番が必要なプレースホルダーは、`{{種別_番号}}` の形式で記述する。

```markdown
{{IMAGE_1}}
{{IMAGE_2}}
{{CODE_1}}
{{CODE_2}}
```

連番が不要な（1つしかない）プレースホルダーは、従来通り番号なしで記述してよい。

```markdown
{{TABLE}}
{{TITLE}}
```

### ファイル側（フォルダ構成）

各フォルダ内のファイル名は、`識別子_番号.拡張子` の形式とする。
番号がない場合（そのvariantにその種別が1つしかない場合）は、
従来通り `識別子.拡張子` のままでよい。

```
images/
├── q1a_1.png      ← q1a の IMAGE_1
├── q1a_2.png      ← q1a の IMAGE_2
tables/
├── q1a.md          ← q1a の TABLE（番号なし＝1つだけ）
snippets/
├── q1a_1.pseudo    ← q1a の CODE_1
├── q1a_2.pseudo    ← q1a の CODE_2
```

## 改修内容

### 1. ファイル名からの識別子・番号の抽出ロジック

ファイル名（拡張子を除いた部分）を解析し、末尾が `_数字` で終わっていれば
「識別子」と「番号」に分割し、そうでなければ番号なしとして扱ってください。

```python
import re
from pathlib import Path
from collections import defaultdict

def parse_filename(stem: str) -> tuple[str, str | None]:
    """
    ファイル名(拡張子なし)から (識別子, 番号) を抽出する。
    例: "q1a_1" -> ("q1a", "1")
        "q1a"   -> ("q1a", None)
    """
    m = re.match(r"^(.+)_(\d+)$", stem)
    if m:
        return m.group(1), m.group(2)
    return stem, None
```

### 2. プレースホルダーキーの決定ロジック

フォルダに対応するプレースホルダー名（`CODE`, `IMAGE`, `TABLE`等）と、
上記で抽出した番号を組み合わせて、最終的なキーを決定してください。

```python
def build_placeholder_key(base_placeholder: str, index: str | None) -> str:
    if index is None:
        return base_placeholder          # 例: "TABLE"
    return f"{base_placeholder}_{index}"  # 例: "IMAGE_1"
```

### 3. variants自動生成処理への統合

既存の `build_variants()` 関数（フォルダ走査でvariantsを組み立てる処理）を、
以下のように変更してください。

```python
def build_variants(folder_to_placeholder: dict) -> dict:
    variants = defaultdict(dict)
    for folder, base_placeholder in folder_to_placeholder.items():
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for f in sorted(folder_path.iterdir()):
            if not f.is_file() or f.name.startswith("."):
                continue
            identifier, index = parse_filename(f.stem)
            key = build_placeholder_key(base_placeholder, index)
            variants[identifier][key] = str(f)
    return variants
```

これにより、`variants["q1a"]` の中身は以下のようになります。

```python
{
    "CODE_1": "snippets/q1a_1.pseudo",
    "CODE_2": "snippets/q1a_2.pseudo",
    "IMAGE_1": "images/q1a_1.png",
    "IMAGE_2": "images/q1a_2.png",
    "TABLE": "tables/q1a.md",
}
```

### 4. 値の変換処理（resolve_value）の対応

既存の `resolve_value()` は、種別判定に `key == "IMAGE"` のような
完全一致を使っている可能性があるため、`IMAGE_1`, `IMAGE_2` のような
連番付きキーでも正しく種別判定できるよう、**先頭部分（ベース種別）で判定する**
形に変更してください。

```python
def resolve_value(key: str, filepath: str) -> str:
    base = re.sub(r"_\d+$", "", key)  # "IMAGE_1" -> "IMAGE"
    if base == "IMAGE":
        return f"![図]({filepath})"
    else:
        return Path(filepath).read_text(encoding="utf-8")
```

今後IMAGE以外にも特殊変換が必要な種別が増えた場合、この `base` 判定に
分岐を追加するだけで対応できる構造にしておいてください。

### 5. 置換処理ループへの影響

既存の「`variants[identifier]` をループしてプレースホルダーを置換する」処理自体は
変更不要です。キーが `IMAGE_1`, `IMAGE_2` のように増えるだけなので、
既存ロジック（`content.replace(f"{{{{{key}}}}}", value)`）がそのまま機能します。

### 6. 未置換プレースホルダーの検出（既存機能の維持）

既存の未置換チェック処理はそのまま維持してください。
`{{IMAGE_1}}` が対応ファイル無しで残っていた場合も、
正しく検出・警告される必要があります。

```python
unresolved = re.findall(r"\{\{(\w+)\}\}", content)
if unresolved:
    print(f"⚠ {identifier}: 未置換のプレースホルダーがあります: {unresolved}")
```

### 7. 欠損時の扱い（既存方針の維持）

前回の改修方針通り、対応ファイルが見つからないプレースホルダーがあっても
**処理を止めず、警告表示のみで継続**してください。
（例：`q1b`には`IMAGE_2`が無い場合でも、`q1b`全体の処理は続行する）

## サンプルファイルの追加

動作確認用に、以下のサンプルファイルを追加作成してください。

- `template.md` に、`{{IMAGE_1}}`, `{{IMAGE_2}}` を含むセクションを
  反映済みのものを用意（ご提示いただいたテンプレート例を参考にしてください）
- `images/q1a_1.png`, `images/q1a_2.png`（ダミーでよい）
- `tables/q1a.md`（番号なしの例として）
- `snippets/q1a_1.pseudo`, `snippets/q1a_2.pseudo`（CODE側の連番例として）

## README.md の更新

`README.md` に以下を追記してください。

- プレースホルダーを複数回使いたい場合は `{{種別_番号}}` の形式で記述すること
- ファイル名も同様に `識別子_番号.拡張子` とすることで対応付けられること
- 番号なしの場合は1つだけのプレースホルダーとして扱われること

修正例：

```markdown
## 同じ種類のプレースホルダーを複数使いたい場合

テンプレート側で番号付きのプレースホルダーを使用してください。

\`\`\`markdown
{{IMAGE_1}}
{{IMAGE_2}}
\`\`\`

対応するファイルも、同じ識別子＋番号の形式で配置します。

\`\`\`
images/q1a_1.png
images/q1a_2.png
\`\`\`

番号を付けない場合（1つだけの場合）は、従来通り番号なしのファイル名・
プレースホルダーで構いません。
```

## 注意事項

- 既存のコマンドライン引数によるテンプレート指定機能は変更しないこと
- 既存のtitles.json連携（`{{TITLE}}`）はこの連番対応と独立した仕組みのまま共存させること
- 文字コードはすべてUTF-8で統一する
- PDFへの変換処理は引き続き本スクリプトの責務外（MD生成まで）とする
- 既存の出力ファイル名ロジック（識別子をそのまま使う）は変更しないこと
