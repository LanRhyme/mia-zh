# mia-zh

Mine in Abyss 客户端汉化模组（Minecraft 1.21.11 / Fabric）

把服务端下发的英文物品名、lore、菜单标题、聊天、计分板按离线词典换成中文，不联网、不上传任何内容

## 为什么不用资源包

MIA 的物品名与 lore 是服务端写进 `item_name` 组件的字面文本，没有 `translate` 键

服务端资源包只有贴图、模型、字体，没有物品文案

资源包只能覆盖语言表，对字面文本无效

## 快速开始

```bash
python3 tools/build_dict.py     # 生成词典
./gradlew build                 # 产物 build/libs/mia-zh-<version>.jar
```

把 jar 放进实例 `mods/` 目录

需要 JDK 21，其余版本已锁在 `gradle.properties`

## 文档

- [交接文档](docs/HANDOFF.md) 现状、构建、词典流水线、数据来源、待办、已知限制
- [词表](tools/mia_glossary.json) 人工维护的事实来源

## 拦截点

| 钩子 | 覆盖 |
| --- | --- |
| `ItemStack#getName` | 物品名、手持名、聊天悬浮名 |
| `ItemStack#getTooltip` | tooltip 全部行，含 lore 与属性 |
| `Entity#getDisplayName` | 生物名牌 |
| `Screen#getTitle` | 容器与菜单标题 |
| `ChatHud#addMessage` | 聊天与系统消息 |
| `InGameHud#setTitle` | 标题、副标题、动作栏 |
| `BossBar#getName` | BOSS 血条 |
| `ScoreboardObjective#getDisplayName` | 计分板标题 |
| `Team#getPrefix` | 计分板侧栏 |
| `HandledScreen#init` | 打开容器时批量采集英文原文 |
