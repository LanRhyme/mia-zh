#!/usr/bin/env python3
"""生成 mia-zh 的默认词典。

输入:
  tools/mia_glossary.json   MIA 专有名词（人工翻译）
  tools/vanilla_en_zh.json  原版英文名 -> 官方中文（由 en_us/zh_cn 对齐而来）

输出:
  src/main/resources/mia-zh/dict.json
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
OUT = ROOT / "src" / "main" / "resources" / "mia-zh" / "dict.json"

# 原版表里这些键不是物品名，翻译它们反而会污染聊天/界面文本
SKIP_PREFIX = (
    "death.", "commands.", "multiplayer.", "options.", "menu.", "key.", "subtitles.",
    "advancements.", "chat.", "selectWorld.", "createWorld.", "resourcepack.", "connect.",
    "disconnect.", "mco.", "narration.", "controls.", "stat.", "build.", "debug.", "help.",
    "argument.", "gamerule.", "mount.", "telemetry.", "datapack.", "pack.", "generator.",
    "structure_block.", "permissions.", "chat_screen.", "soundCategory.", "jigsaw.", "itemGroup.",
)
# 只保留这些前缀的键（物品/方块/实体/效果/附魔/药水），保证替换只落在名词上
KEEP_PREFIX = (
    "item.minecraft.", "block.minecraft.", "entity.minecraft.", "effect.minecraft.",
    "enchantment.minecraft.", "itemGroup.minecraft.", "painting.minecraft.", "banner.",
    "music_disc.", "potion.", "particle.minecraft.",
)

# 词条优先级：MIA 人工翻译 > 原版官方译名
def build_entries() -> dict:
    glossary = json.loads((TOOLS / "mia_glossary.json").read_text(encoding="utf-8"))
    vanilla = json.loads((TOOLS / "vanilla_en_zh.json").read_text(encoding="utf-8"))

    entries = {}
    for en, zh in vanilla.items():
        if not en or not zh or en == zh:
            continue
        if len(en) < 2 or len(en) > 80:
            continue
        # 原版表是「英文显示名 -> 中文」，这里只收看起来像名词的
        if not re.search(r"[A-Za-z]", en):
            continue
        entries[en] = zh

    for group in ("items", "mobs", "ui"):
        for en, zh in glossary.get(group, {}).items():
            entries[en] = zh
    return entries


PATTERNS = [
    # 属性行（MIA lore 里最常见的形式）
    {"pattern": r"^Damage:?\s*(.+)$", "replace": "伤害：$1"},
    {"pattern": r"^Durability:?\s*(.+)$", "replace": "耐久：$1"},
    {"pattern": r"^Defense:?\s*(.+)$", "replace": "防御：$1"},
    {"pattern": r"^Armor:?\s*(.+)$", "replace": "护甲：$1"},
    {"pattern": r"^Weight:?\s*(.+)$", "replace": "重量：$1"},
    {"pattern": r"^Price:?\s*(.+)$", "replace": "价格：$1"},
    {"pattern": r"^Value:?\s*(.+)$", "replace": "价值：$1"},
    {"pattern": r"^Rarity:?\s*(.+)$", "replace": "稀有度：$1"},
    {"pattern": r"^Tier:?\s*(.+)$", "replace": "阶级：$1"},
    {"pattern": r"^Level:?\s*(.+)$", "replace": "等级：$1"},
    {"pattern": r"^Health:?\s*(.+)$", "replace": "生命：$1"},
    {"pattern": r"^Food:?\s*(.+)$", "replace": "食物：$1"},
    {"pattern": r"^Nutrition:?\s*(.+)$", "replace": "营养：$1"},
    {"pattern": r"^Saturation:?\s*(.+)$", "replace": "饱和度：$1"},
    {"pattern": r"^Effects?:?\s*(.+)$", "replace": "效果：$1"},
    {"pattern": r"^Requires:?\s*(.+)$", "replace": "需求：$1"},
    {"pattern": r"^Use:?\s*(.+)$", "replace": "用途：$1"},
    {"pattern": r"^Ability:?\s*(.+)$", "replace": "能力：$1"},
    {"pattern": r"^Chance:?\s*(.+)$", "replace": "概率：$1"},
    {"pattern": r"^Amount:?\s*(.+)$", "replace": "数量：$1"},
    {"pattern": r"^Cooldown:?\s*(.+)$", "replace": "冷却：$1"},
    {"pattern": r"^Range:?\s*(.+)$", "replace": "范围：$1"},
    {"pattern": r"^Speed:?\s*(.+)$", "replace": "速度：$1"},
    {"pattern": r"^Layer\s*(\d+)$", "replace": "第 $1 层"},
    {"pattern": r"^Layer:?\s*(\d+)$", "replace": "层数：$1"},
    # 常见动作提示
    {"pattern": r"^Right[- ]click to use$", "replace": "右键使用"},
    {"pattern": r"^Right[- ]click to place$", "replace": "右键放置"},
    {"pattern": r"^Shift \+ Right[- ]click to (.+)$", "replace": "Shift + 右键$1"},
    {"pattern": r"^Press (.+) to use$", "replace": "按 $1 使用"},
]


def main() -> None:
    entries = build_entries()
    payload = {
        "version": 1,
        "enabled": True,
        "harvest": True,
        "_comment": "MIA 汉化词典：entries 为精确匹配，patterns 为正则（$1 取分组）。改 user.json 可覆盖本文件。",
        "entries": dict(sorted(entries.items(), key=lambda kv: kv[0].lower())),
        "patterns": PATTERNS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"写出 {OUT}  ({len(entries)} 条词条 / {len(PATTERNS)} 条规则, {OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
