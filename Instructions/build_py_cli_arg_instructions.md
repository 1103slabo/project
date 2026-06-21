# build.py 改修指示書：テンプレートファイルをコマンドライン引数で指定可能にする

## 概要

現在 `build.py` は `template.md` というファイル名を直接コード内で
読み込んでいますが、今後テンプレートファイルが複数になる予定のため、
**コマンドライン引数で対象テンプレートファイルを指定できる**ように改修してください。

## 改修内容

### 1. コマンドライン引数の受け取り

`argparse` を使い、テンプレートファイルのパスを引数として受け取れるようにしてください。

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="テンプレートMDにコード等を差し込んでバリエーションMDを生成する"
    )
    parser.add_argument(
        "template",
        help="使用するテンプレートMDファイルのパス（例: templates/template_a.md）"
    )
    return parser.parse_args()
```

### 2. 既存の固定読み込み処理の置き換え

現状おそらく以下のようにファイル名が固定で書かれている箇所を：

```python
template = Path("template.md").read_text(encoding="utf-8")
```

引数から受け取ったパスを使う形に変更してください：

```python
args = parse_args()
template_path = Path(args.template)
template = template_path.read_text(encoding="utf-8")
```

### 3. テンプレートファイルが存在しない場合のエラーハンドリング

指定されたテンプレートファイルが存在しない場合、分かりやすいエラーメッセージを表示して
スクリプトを終了してください（既存のtry/exceptパターンがあればそれに合わせる）。

```python
if not template_path.exists():
    print(f"✗ 指定されたテンプレートファイルが見つかりません: {template_path}")
    raise SystemExit(1)
```

### 4. 実行コマンドの例

改修後、以下のように実行できることを確認してください。

```bash
python build.py template.md
python build.py templates/template_kanji_mondai.md
```

引数を省略した場合は、`argparse` の標準動作として
使い方（usage）メッセージが表示されれば問題ありません
（デフォルト値を設定する必要はありません）。

### 5. variants辞書（スニペット指定）との関係について

`variants` 辞書（プレースホルダーとスニペットファイルの対応表）は、
このコマンドライン引数化とは独立した仕組みのままで構いません。
つまり「どのテンプレートを使うか」と「どのスニペットを差し込むか」は
別々に管理される設計のままで問題ありません
（variants自体を動的に切り替える機能は今回のスコープ外です）。

### 6. README.md の更新

`README.md` の「使い方」セクションに、コマンドライン引数の指定が
必須になったことを反映してください。

修正例：

```markdown
## 使い方

\`\`\`bash
python build.py <テンプレートファイルのパス>
\`\`\`

例:
\`\`\`bash
python build.py template.md
python build.py templates/template_b.md
\`\`\`

新しいテンプレートを追加する場合は、テンプレートファイルを作成し、
実行時にそのパスを引数として指定するだけで利用できます。
```

## 注意事項

- 既存の出力ファイル名生成ロジック（`output/<variant名>.md` など）には影響を与えないこと
- 既存のプレースホルダー置換ロジック・エラーハンドリング・サマリ表示機能はそのまま維持すること
- 文字コードはすべてUTF-8で統一する
- 引数処理以外の既存ロジックは変更しないこと
