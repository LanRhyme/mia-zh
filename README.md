# mia-zh

Mine in Abyss 服务器物品与界面的客户端汉化模组

## 为什么需要它

MIA 的内容全部由服务端下发，物品名是服务端把 MiniMessage 字面量直接塞进 `item_name` 组件的结果
服务端代码没有 `translate` 键，也没有任何 locale 支持
资源包只能覆盖语言表，对字面文本无效，所以常规汉化资源包在 MIA 服务器上不起作用

本模组在客户端拦截文本组件，按离线词典把英文换成中文，不联网、不上传任何内容

## 安装

把 `build/libs/mia-zh-0.1.0.jar` 放进实例的 `mods/` 目录即可
需要 Minecraft 1.21.11 与 Fabric Loader 0.18 以上

## 配置目录

首次启动后在实例的 `config/mia-zh/` 生成

| 文件 | 作用 |
| --- | --- |
| `dict.json` | 内置词典，随模组更新覆盖 |
| `user.json` | 用户覆盖表，格式同 `dict.json`，同名条目优先 |
| `harvest.txt` | 未命中的原始英文，按出现次数排序，用于补翻译 |

`user.json` 例

```json
{
  "entries": {
    "Star Compass": "星之罗盘"
  },
  "patterns": [
    { "pattern": "^Damage: (.+)$", "replace": "伤害：$1" }
  ]
}
```

改完存盘 2 秒内自动重载，不用重启游戏

## 拦截点

| 钩子 | 覆盖内容 |
| --- | --- |
| `ItemStack#getName` | 物品名、手上物品名、聊天栏物品悬浮名 |
| `ItemStack#getTooltip` | tooltip 全部行，含 lore 与属性行 |
| `Entity#getDisplayName` | 生物名牌与实体显示名 |
| `Screen#getTitle` | 容器与菜单标题 |
| `ChatHud#addMessage` | 聊天与系统消息 |
| `InGameHud#setTitle` | 大标题、副标题、动作栏 |
| `BossBar#getName` | BOSS 血条标题 |
| `ScoreboardObjective#getDisplayName` | 计分板目标标题 |
| `Team#getPrefix` | 计分板侧栏前后缀与整行 |

## 工作流

1. 先进服玩十分钟，`harvest.txt` 会记录所有没命中的英文
2. 把 `harvest.txt` 里的条目翻成中文，写进 `user.json`
3. 专有名词长期沉淀进 `tools/mia_glossary.json`，重新生成 `dict.json`

## 构建

```bash
python3 tools/build_dict.py     # 合成词典，需要 tools/ 下的两张表
./gradlew build                 # 产物在 build/libs/
```

`tools/vanilla_en_zh.json` 由原版 `en_us.json` 与 `zh_cn.json` 按 key 对齐生成，只保留物品、方块、实体、效果、附魔、药水等名词键

## 数据来源

MIA 词表来自 wiki 的物品页与生物掉落表，生物名以意译优先，无法意译的用音译
原版名词使用官方中文译名
