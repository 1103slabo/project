import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Windowsのコンソールで Unicode 記号を出力できるよう UTF-8 に設定する
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FOLDER_TO_PLACEHOLDER = {
    "snippets": "CODE",
    "images": "IMAGE",
    "tables": "TABLE",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="テンプレートMDにコード等を差し込んでバリエーションMDを生成する"
    )
    parser.add_argument(
        "template",
        help="使用するテンプレートMDファイルのパス（例: templates/template_a.md）"
    )
    return parser.parse_args()


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


def build_placeholder_key(base_placeholder: str, index: str | None) -> str:
    if index is None:
        return base_placeholder
    return f"{base_placeholder}_{index}"


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


def resolve_value(key: str, filepath: str) -> str:
    """プレースホルダー種別に応じてファイルの中身を変換して返す。"""
    base = re.sub(r"_\d+$", "", key)
    if base == "IMAGE":
        return f"![図]({filepath})"
    else:
        return Path(filepath).read_text(encoding="utf-8")


args = parse_args()
template_path = Path(args.template)

if not template_path.exists():
    print(f"✗ 指定されたテンプレートファイルが見つかりません: {template_path}")
    raise SystemExit(1)

# 対応表を読み込む
titles = json.loads(Path("titles.json").read_text(encoding="utf-8"))

# output/ フォルダがなければ作成
Path("output").mkdir(exist_ok=True)

# テンプレートを読み込む
template = template_path.read_text(encoding="utf-8")

# フォルダ構造から variants を自動生成
variants = build_variants(FOLDER_TO_PLACEHOLDER)

results = []

for identifier, parts in sorted(variants.items()):
    try:
        warnings = []

        # {{TITLE}} の置換（titles.json を参照）
        title_key = re.sub(r"^\d+_", "", identifier)
        title = titles.get(title_key, identifier)
        content = template.replace("{{TITLE}}", title)

        # テンプレート内のプレースホルダーを検出し、対応ファイルがあれば置換
        placeholders_in_template = re.findall(r"\{\{(\w+)\}\}", template)
        for placeholder in set(placeholders_in_template):
            if placeholder == "TITLE":
                continue
            if placeholder in parts:
                value = resolve_value(placeholder, parts[placeholder])
                content = content.replace(f"{{{{{placeholder}}}}}", value)
            else:
                print(f"⚠ {identifier}: {placeholder} に対応するファイルがありません（スキップ）")
                warnings.append(placeholder)

        # 未置換プレースホルダーの検出
        unresolved = re.findall(r"\{\{(\w+)\}\}", content)
        if unresolved:
            print(f"⚠ {identifier}: 未置換のプレースホルダーがあります: {unresolved}")

        output_path = Path("output") / f"{identifier}.md"
        output_path.write_text(content, encoding="utf-8")

        if warnings:
            warn_str = "、".join(f"{w}未対応" for w in warnings)
            print(f"⚠ {identifier}: {output_path} を生成しました（{warn_str}）")
            results.append(f"⚠ {identifier}: {output_path} を生成しました（{warn_str}）")
        else:
            print(f"✓ {identifier}: {output_path} を生成しました")
            results.append(f"✓ {identifier}: {output_path} を生成しました")

    except Exception as e:
        print(f"✗ {identifier}: 予期しないエラーが発生しました ({e})")
        results.append(f"✗ {identifier}: 予期しないエラー ({e})")

print()
print("=== 処理結果 ===")
for line in results:
    print(line)
