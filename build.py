import json
import re
import sys
from pathlib import Path

# Windowsのコンソールで Unicode 記号を出力できるよう UTF-8 に設定する
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 対応表を読み込む
titles = json.loads(Path("titles.json").read_text(encoding="utf-8"))

# output/ フォルダがなければ作成
Path("output").mkdir(exist_ok=True)

# テンプレートを読み込む
template = Path("template.md").read_text(encoding="utf-8")

# variant名 → {プレースホルダー名: ファイルパス} の辞書
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


def resolve_value(key: str, filepath: str) -> str:
    """プレースホルダー種別に応じてファイルの中身を変換して返す。"""
    if key == "IMAGE":
        return f"![図]({filepath})"
    else:
        return Path(filepath).read_text(encoding="utf-8")


results = []

for name, parts in variants.items():
    try:
        # {{TITLE}} の置換（titles.json を参照）
        title_key = re.sub(r"^\d+_", "", name)
        title = titles.get(title_key, name)
        content = template.replace("{{TITLE}}", title)

        # 各プレースホルダーをループして汎用置換
        skip = False
        for key, filepath in parts.items():
            try:
                value = resolve_value(key, filepath)
            except FileNotFoundError:
                print(f"✗ {name}: ファイルが見つかりません: {filepath}")
                results.append(f"✗ {name}: スキップ（ファイル未検出: {filepath}）")
                skip = True
                break

            content = content.replace(f"{{{{{key}}}}}", value)

        if skip:
            continue

        # 未置換プレースホルダーの検出
        unresolved = re.findall(r"\{\{(\w+)\}\}", content)
        if unresolved:
            print(f"⚠ {name}: 未置換のプレースホルダーがあります: {unresolved}")

        out_md = Path("output") / f"{name}.md"
        out_md.write_text(content, encoding="utf-8")
        print(f"✓ {name}: {out_md} を生成しました")
        results.append(f"✓ {name}: {out_md} を生成しました")

    except Exception as e:
        print(f"✗ {name}: 予期しないエラーが発生しました ({e})")
        results.append(f"✗ {name}: 予期しないエラー ({e})")

print()
print("=== 処理結果 ===")
for line in results:
    print(line)
