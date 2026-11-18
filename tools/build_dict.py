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

    for group in ("items", "mobs", "ui", "lore", "poi"):
        for en, zh in glossary.get(group, {}).items():
            entries[en] = zh

    # 别名：服务端把「X Cooked」写成「Cooked X」这类语序，两种都要能命中
    for en, zh in list(entries.items()):
        for suffix in (" Cooked", " Raw", " Roasted", " Uncooked"):
            if en.endswith(suffix):
                base = en[: -len(suffix)]
                entries.setdefault(suffix.strip() + " " + base, zh)
                break
    # 别名：连字符与空格的写法都收
    for en, zh in list(entries.items()):
        if "-" in en:
            entries.setdefault(en.replace("-", " "), zh)
        elif " " in en:
            entries.setdefault(en.replace(" ", "-"), zh)
    return entries


PATTERNS = [
    # 成套物品（护甲/工具/装饰）按家族拼装，避免逐条硬编码
    {"pattern": r"^Carved (.+)$", "replace": "雕刻$1"},
    {"pattern": r"^Build-Server Marker Block (.+)$", "replace": "建造服标记方块·$1"},
    {"pattern": r"^Armor Upgrade: (.+)$", "replace": "护甲升级：$1"},
    {"pattern": r"^Heavy Delving (.+)$", "replace": "重型探窟$1"},
    {"pattern": r"^Light Delving (.+)$", "replace": "轻型探窟$1"},
    {"pattern": r"^Orphan Delving (.+)$", "replace": "孤儿院探窟$1"},
    {"pattern": r"^Orphanage Issued (.+)$", "replace": "孤儿院配发$1"},
    {"pattern": r"^Stingerhead (.+)$", "replace": "刺头$1"},
    {"pattern": r"^Charcoal Sand (.+)$", "replace": "炭沙$1"},
    {"pattern": r"^Gold (.+)$", "replace": "金$1"},
    {"pattern": r"^Cooked (.+)$", "replace": "熟$1"},
    {"pattern": r"^Raw (.+)$", "replace": "生$1"},
    {"pattern": r"^Roasted (.+)$", "replace": "烤$1"},
    {"pattern": r"^Baked (.+)$", "replace": "烤$1"},
    {"pattern": r"^Chiseled (.+)$", "replace": "雕纹$1"},
    {"pattern": r"^Polished (.+)$", "replace": "磨制$1"},
    {"pattern": r"^Packed Ice (.+)$", "replace": "浮冰$1"},
    {"pattern": r"^(.*) Hatchet$", "replace": "$1手斧"},
    {"pattern": r"^(.*) Sickle$", "replace": "$1镰"},
    {"pattern": r"^(.*) Pickaxe$", "replace": "$1镐"},
    {"pattern": r"^(.*) Shovel$", "replace": "$1锹"},
    {"pattern": r"^(.*) Chestplate$", "replace": "$1胸甲"},
    {"pattern": r"^(.*) Leggings$", "replace": "$1护腿"},
    {"pattern": r"^(.*) Helmet$", "replace": "$1头盔"},
    {"pattern": r"^(.*) Boots$", "replace": "$1靴"},
    {"pattern": r"^(.*) Pattern$", "replace": "$1图案"},
    # 属性行（MIA lore 里最常见的形式）
    {"pattern": r"^Damage:?\s*(.+)$", "replace": "伤害：$1"},
    {"pattern": r"^Durability:?\s*(.+)$", "replace": "耐久：$1"},
    {"pattern": r"^Defense:?\s*(.+)$", "replace": "防御：$1"},
    {"pattern": r"^Armor:?\s*(.+)$", "replace": "护甲：$1"},
    {"pattern": r"^Attack Damage:?\s*(.+)$", "replace": "攻击伤害：$1"},
    {"pattern": r"^Attack Speed:?\s*(.+)$", "replace": "攻击速度：$1"},
    {"pattern": r"^Max Health:?\s*(.+)$", "replace": "最大生命：$1"},
    {"pattern": r"^Movement Speed:?\s*(.+)$", "replace": "移动速度：$1"},
    {"pattern": r"^Mining Speed:?\s*(.+)$", "replace": "挖掘速度：$1"},
    {"pattern": r"^Armor Toughness:?\s*(.+)$", "replace": "盔甲韧性：$1"},
    {"pattern": r"^Knockback Resistance:?\s*(.+)$", "replace": "击退抗性：$1"},
    {"pattern": r"^Luck:?\s*(.+)$", "replace": "幸运：$1"},
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

    {"pattern": r"^in the (.+)$", "replace": "（$1）"},
    {"pattern": r"^in (.+)$", "replace": "在$1"},
    {"pattern": r"^You hear whispers that (.+) has obtained a (.+) relic\.$", "replace": "你听到低语：$1 获得了一件$2遗物。"},
    {"pattern": r"^Unable to use Axiom.*$", "replace": "无法使用 Axiom：你的版本过旧，请更新到最新版才能在本服使用"},
    {"pattern": r"^([A-Za-z][A-Za-z' \-]*) (\d+)/(\d+)$", "replace": "$1 $2/$3"},
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
