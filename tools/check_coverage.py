#!/usr/bin/env python3
"""比对词典与服务端内容，列出没翻译的条目

用法：
  python3 tools/check_coverage.py            # 打印统计
  python3 tools/check_coverage.py --todo     # 同时把待翻条目写进 tools/todo_*.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
DICT = ROOT / "src" / "main" / "resources" / "mia-zh" / "dict.json"


def java_replacement(replace: str) -> str:
    """把 Java 的 $1 换成 Python 的 \\g<1>"""
    return re.sub(r"\$(\d)", r"\\g<\1>", replace)


def load_dict():
    data = json.loads(DICT.read_text(encoding="utf-8"))
    entries = data["entries"]
    patterns = [(re.compile(p["pattern"]), p["replace"]) for p in data.get("patterns", [])]
    return entries, patterns


def resolve(text: str, entries: dict, patterns, depth: int = 0):
    if text in entries:
        return entries[text]
    stripped = text.strip()
    if stripped in entries:
        return entries[stripped]
    body = re.sub("\u00a7.", "", stripped)
    if body in entries:
        return entries[body]
    if depth >= 3:
        return None
    for pattern, replace in patterns:
        match = pattern.fullmatch(body)
        if not match:
            continue
        out = match.expand(java_replacement(replace))
        for group in match.groups():
            if not group or group == body:
                continue
            translated = resolve(group, entries, patterns, depth + 1)
            if translated:
                out = out.replace(group, translated)
        return out
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", action="store_true", help="把未翻译条目写成 todo json")
    args = ap.parse_args()

    if not DICT.exists():
        sys.exit(f"缺少词典 {DICT}，先跑 python3 tools/build_dict.py")
    entries, patterns = load_dict()

    names_path = TOOLS / "content_names.json"
    lore_path = TOOLS / "content_lore.json"
    if not names_path.exists() or not lore_path.exists():
        sys.exit("缺少 content_*.json，先跑 python3 tools/fetch_content.py")

    names = json.loads(names_path.read_text(encoding="utf-8"))
    lore = json.loads(lore_path.read_text(encoding="utf-8"))

    miss_names = [n for n in names if resolve(n, entries, patterns) is None]
    miss_lore = [l for l in lore if resolve(l, entries, patterns) is None]

    def pct(miss, total):
        return f"{(total - len(miss)) * 100 // max(total, 1)}%"

    print(f"词典 {len(entries)} 条词条 / {len(patterns)} 条规则")
    print(f"物品名 {len(names)} 条，未翻译 {len(miss_names)} 条（覆盖 {pct(miss_names, len(names))}）")
    print(f"lore   {len(lore)} 条，未翻译 {len(miss_lore)} 条（覆盖 {pct(miss_lore, len(lore))}）")
    if miss_names:
        print("\n未翻译物品名：")
        for name in miss_names[:30]:
            print("  ", name)
    if miss_lore:
        print("\n未翻译 lore 示例：")
        for line in miss_lore[:20]:
            print("  ", line)

    if args.todo:
        (TOOLS / "todo_names.json").write_text(
            json.dumps({n: "" for n in miss_names}, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        (TOOLS / "todo_lore.json").write_text(
            json.dumps({l: "" for l in miss_lore}, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"\n待翻清单 -> {TOOLS/'todo_names.json'} / {TOOLS/'todo_lore.json'}")


if __name__ == "__main__":
    main()
