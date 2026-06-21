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
