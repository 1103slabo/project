# 修正指示書

## 目的
`build.py` と `template.md` を修正し、各スニペットファイルから生成される Markdown のタイトル(`# 問題`の部分)を、ファイル名に応じた日本語タイトルに自動で置き換えられるようにする。また、対応表(英語名→日本語名)を別ファイルで管理する。

## 変更対象ファイル
- `template.md`
- `build.py`
- `titles.json`(新規作成)

---

## 1. `template.md` の修正

先頭の見出し `# 問題` を `# {{TITLE}}` に変更する。

### 変更前
```markdown
# 問題

次のプログラムを読み、設問に答えよ。
```

### 変更後
```markdown
# {{TITLE}}

次のプログラムを読み、設問に答えよ。
```

それ以外の部分(`{{CODE}}` を含む箇所など)は変更しない。

---

## 2. `titles.json` の新規作成

プロジェクトルートに `titles.json` を作成し、スニペットファイル名(先頭の数字とアンダースコアを除いた部分)をキー、日本語タイトルを値とする対応表を定義する。

### 例
```json
{
  "array_search": "配列探索",
  "bubble_sort": "バブルソート"
}
```

- `snippets/` ディレクトリ内の実際のファイル名を確認し、対応するキーをすべて作成すること。
- 日本語訳が不明な場合は、いったん英語名のままでよい(後で修正可能)。

---

## 3. `build.py` の修正

以下の点を修正する。

1. `titles.json` を読み込む処理を追加する。
2. 各スニペットファイルについて、ファイル名(`snippet.stem`)から先頭の「数字+アンダースコア」を正規表現で除去し、対応表のキーとする。
3. 対応表からタイトルを取得する。キーが対応表に存在しない場合は、キーそのもの(英語名)を使用する。
4. テンプレート内の `{{TITLE}}` を取得したタイトルで置換する。

### 修正後の全体コード

```python
import json
import re
from pathlib import Path

snippets_dir = Path("snippets")

# 対応表を読み込む
titles = json.loads(Path("titles.json").read_text(encoding="utf-8"))

# output/ フォルダがなければ作成
Path("output").mkdir(exist_ok=True)

# テンプレートを読み込む
template = Path("template.md").read_text(encoding="utf-8")

for snippet in sorted(snippets_dir.glob("*.pseudo")):
    name = snippet.stem
    try:
        # ファイル名先頭の「数字＋アンダースコア」を除いたキーでタイトルを取得
        key = re.sub(r"^\d+_", "", name)
        title = titles.get(key, key)  # 対応表に無ければキーそのまま使用

        # {{TITLE}}・{{CODE}} を置換して output/ に書き出す
        code = snippet.read_text(encoding="utf-8")
        content = template.replace("{{TITLE}}", title)
        content = content.replace("{{CODE}}", code)
        out_md = Path("output") / f"{name}.md"
        out_md.write_text(content, encoding="utf-8")

        print(f"[OK]   {name}: {out_md} を生成しました")

    except Exception as e:
        # 予期しないエラーが発生しても他のバリエーションの処理を続ける
        print(f"[FAIL] {name}: 予期しないエラーが発生しました ({e})")
```

---

## 4. 動作確認

修正後、以下を実行して期待通りに動作することを確認する。

```bash
python build.py
```

- `output/` 配下に各スニペットに対応する `.md` ファイルが生成されること。
- 各ファイルの先頭見出しが、`titles.json` に登録された日本語タイトル(未登録の場合は英語名)になっていること。
- `{{CODE}}` の部分にスニペットの内容が正しく挿入されていること。
- エラーが発生したスニペットがあれば `[FAIL]` メッセージが出力され、他のスニペットの処理は継続されること。
