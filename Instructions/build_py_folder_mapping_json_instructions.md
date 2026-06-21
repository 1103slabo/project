# build.py 改修指示書：FOLDER_TO_PLACEHOLDER の外部ファイル化（JSON）

## 概要

現在 `build.py` 内にハードコードされている `FOLDER_TO_PLACEHOLDER` 辞書を、
外部のJSONファイルに切り出してください。
これにより、フォルダ・プレースホルダーの対応関係を追加・変更する際に
`build.py` 自体を編集する必要がなくなります。

## 改修内容

### 1. 設定ファイル `folder_mapping.json` の新規作成

プロジェクトルートに `folder_mapping.json` を作成し、
現在ハードコードされている内容をそのまま移してください。

```json
{
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE"
}
```

### 2. build.py側の読み込み処理

`build.py` 内の固定辞書定義：

```python
FOLDER_TO_PLACEHOLDER = {
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE",
}
```

これを削除し、JSONファイルから読み込む関数に置き換えてください。

```python
import json
from pathlib import Path

def load_folder_mapping(config_path: str = "folder_mapping.json") -> dict:
    path = Path(config_path)
    if not path.exists():
        print(f"✗ 設定ファイルが見つかりません: {config_path}")
        raise SystemExit(1)
    with path.open(encoding="utf-8") as f:
        return json.load(f)
```

呼び出し側（`main`関数やスクリプト本体）で以下のように使用してください。

```python
FOLDER_TO_PLACEHOLDER = load_folder_mapping()
```

### 3. JSON読み込み失敗時のエラーハンドリング

JSONの構文エラーなど、パースに失敗した場合も分かりやすいメッセージを出して
終了するようにしてください。

```python
def load_folder_mapping(config_path: str = "folder_mapping.json") -> dict:
    path = Path(config_path)
    if not path.exists():
        print(f"✗ 設定ファイルが見つかりません: {config_path}")
        raise SystemExit(1)
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"✗ 設定ファイルの形式が正しくありません: {config_path}")
        print(f"  詳細: {e}")
        raise SystemExit(1)
```

### 4. 設定ファイルのパスをコマンドライン引数で変更可能にする（任意・推奨）

既存の `argparse` 設定（テンプレートファイル指定）に、
オプション引数として設定ファイルパスも指定できるようにしてください。
省略時はデフォルトで `folder_mapping.json` を使う形にします。

```python
parser.add_argument(
    "--mapping",
    default="folder_mapping.json",
    help="フォルダ⇔プレースホルダー対応設定ファイルのパス（デフォルト: folder_mapping.json）"
)
```

呼び出し側：

```python
args = parse_args()
FOLDER_TO_PLACEHOLDER = load_folder_mapping(args.mapping)
```

これにより、プロジェクトや科目ごとに異なる `folder_mapping.json` を
切り替えて使うことも可能になります（例: `--mapping mapping_kanji.json`）。

### 5. 既存ロジックへの影響

`FOLDER_TO_PLACEHOLDER` を参照している既存の `build_variants()` 関数などは、
変数の中身の構造（`{フォルダ名: プレースホルダー名}`）自体は変わらないため、
**呼び出し部分の変更は不要**です。読み込み元が固定辞書からJSON読み込みに
変わるだけです。

## README.md の更新

`README.md` に以下を追記してください。

- `folder_mapping.json` でフォルダとプレースホルダーの対応を管理していること
- 新しい種別（フォルダ）を追加したい場合は、`build.py`を編集せず
  `folder_mapping.json` にエントリを追加すればよいこと

修正例：

```markdown
## フォルダとプレースホルダーの対応設定

`folder_mapping.json` で、どのフォルダがどのプレースホルダーに対応するかを管理しています。

\`\`\`json
{
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE"
}
\`\`\`

新しい種類のファイル（例: 音声、グラフ等）を追加したい場合は、
対応するフォルダを作成し、このJSONにエントリを追加するだけで使えるようになります。

\`\`\`json
{
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE",
    "graphs": "GRAPH"
}
\`\`\`

設定ファイルのパスを変更したい場合は、\`--mapping\` オプションで指定できます。

\`\`\`bash
python build.py template.md --mapping mapping_kanji.json
\`\`\`
```

## 注意事項

- 既存のコマンドライン引数（テンプレート指定）の動作は変更しないこと
- 既存のvariants自動生成ロジック、連番プレースホルダー対応ロジックには影響を与えないこと
- 文字コードはすべてUTF-8で統一する
- `folder_mapping.json` のサンプルファイル自体もプロジェクトルートに作成しておくこと
