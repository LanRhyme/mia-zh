#!/usr/bin/env python3
"""从 MineInAbyss/server-config 抓取服务端真实的物品名与 lore 原文

MIA 的服务端内容配置是公开的，物品名与 lore 都以 MiniMessage 写在
set.item 组件的 itemName / lore 字段里，这就是客户端实际收到的文本来源

用法：
  python3 tools/fetch_content.py            # 克隆或更新到 ~/tmp/mia-config
  python3 tools/fetch_content.py --repo /path/to/server-config

输出：
  tools/content_items.json  { "物品名": ["lore 行", ...], ... }
  tools/content_names.json  ["物品名", ...]
  tools/content_lore.json   ["lore 行", ...]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
REPO_URL = "https://github.com/MineInAbyss/server-config.git"
DEFAULT_REPO = Path.home() / "tmp" / "mia-config"

TAG = re.compile(r"<[^<>]*>")


def clean(text: str) -> str:
    """去掉 MiniMessage 标签与换行标记，只留纯文本"""
    text = text.strip()
    text = re.sub(r"<newline>|<br\s*/?>", " ", text)
    text = TAG.sub("", text)
    text = text.replace("&amp;", "&").replace("\\&", "&")
    return text.strip()


def ensure_repo(repo: Path) -> Path:
    if (repo / ".git").exists():
        print(f"更新 {repo}")
        subprocess.run(["git", "-C", str(repo), "pull", "--ff-only", "--depth", "1"], check=False)
        return repo
    repo.parent.mkdir(parents=True, exist_ok=True)
    print(f"克隆到 {repo}")
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(repo)], check=True)
    return repo


def walk(node, items: dict) -> None:
    if isinstance(node, dict):
        name = node.get("itemName")
        lines = node.get("lore")
        if isinstance(name, str):
            key = clean(name)
            if key:
                bucket = items.setdefault(key, [])
                if isinstance(lines, list):
                    for line in lines:
                        if isinstance(line, str):
                            body = clean(line)
                            if body and body not in bucket:
                                bucket.append(body)
        for value in node.values():
            walk(value, items)
    elif isinstance(node, list):
        for value in node:
            walk(value, items)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    args = ap.parse_args()

    try:
        import yaml  # noqa: WPS433
    except ImportError:
        sys.exit("需要 PyYAML: python3 -m pip install pyyaml")

    repo = ensure_repo(args.repo)
    items: dict = {}
    files = 0
    failed = 0
    for path in repo.rglob("*.yml"):
        if "/.git/" in str(path):
            continue
        files += 1
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            failed += 1
            continue
        walk(doc, items)

    items = {k: v for k, v in items.items() if re.search(r"[A-Za-z]{2}", k)}
    lore = sorted({line for lines in items.values() for line in lines})

    TOOLS.mkdir(parents=True, exist_ok=True)
    (TOOLS / "content_items.json").write_text(
        json.dumps(dict(sorted(items.items())), ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (TOOLS / "content_names.json").write_text(
        json.dumps(sorted(items), ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (TOOLS / "content_lore.json").write_text(
        json.dumps(lore, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"扫描 {files} 个 yml（解析失败 {failed}）")
    print(f"物品名 {len(items)} 条，lore 行 {len(lore)} 条")
    print(f"输出 -> {TOOLS/'content_items.json'}")


if __name__ == "__main__":
    main()
