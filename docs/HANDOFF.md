# 交接文档

mia-zh 是一个 Minecraft 1.21.11 Fabric 客户端模组，用来把 Mine in Abyss 服务器下发的英文文本换成中文

## 为什么需要它

MIA 的物品名与 lore 是服务端把 MiniMessage 字面量直接写进 `item_name` 与 lore 组件的，没有 `translate` 键，也没有 locale 支持

服务端资源包（下载后 33 MB / 7078 文件）只有贴图、模型、字体，`assets/*/lang/` 只有 6 个文件且都不是物品文案

所以资源包汉化路线无效，只能在客户端拦截文本组件查离线词典

## 当前状态

| 项 | 数值 |
| --- | --- |
| 物品名覆盖 | 429 / 429，100% |
| lore 覆盖 | 132 / 515，25% |
| 词典词条 | 6496 |
| 正则规则 | 68 |
| Mixin 拦截点 | 9 个 |
| 运行期异常 | 0 |

未翻译的 383 条 lore 全部在 `tools/todo_lore.json`，键是英文原文，值留空待填

## 目录结构

```
src/main/java/dev/lanrhyme/miazh/
  MiaZhClient.java        客户端入口
  Translator.java         词典加载 + 查表 + 正则 + 参数翻译 + 采集
  mixin/                  9 个拦截点
src/main/resources/
  fabric.mod.json         模组元数据
  miazh.mixins.json       Mixin 清单
  mia-zh/dict.json        构建产物，由 tools/build_dict.py 生成
tools/
  mia_glossary.json       人工词表，物品 / 生物 / 地名 / lore / UI
  vanilla_en_zh.json      原版名词表，en_us 与 zh_cn 按 key 对齐
  build_dict.py           合成 dict.json，含别名与家族规则
  fetch_content.py        从 server-config 仓库抓全部物品名与 lore
  check_coverage.py       比对覆盖率，可导出待翻清单
  patch_flclash_rule.py   给 FlClash 补 mineinabyss 直连规则
```

## 构建

依赖 JDK 21（Gradle 与 Loom 1.11.8 都跑在 21 上）

```bash
python3 tools/fetch_content.py      # 拉服务端内容，可选，用来对覆盖率
python3 tools/build_dict.py         # 生成 dict.json
./gradlew build                     # 产物 build/libs/mia-zh-<version>.jar
```

`gradle.properties` 里锁定了 mc 1.21.11 / loader 0.18.4 / yarn 1.21.11+build.6 / loom 1.11.8，Gradle wrapper 是 8.14.3

Loom 1.19 需要 JVM 25 且对 1.21.11 拒绝 `officialMojangMappings()`，所以不要升 Loom

## 词典流水线

1. `tools/mia_glossary.json` 是人工维护的事实来源，改完跑 `build_dict.py`
2. `build_dict.py` 会合并原版名词表，自动生成 `Cooked X` / `X Cooked` 双向别名、连字符与空格变体
3. 成套物品走正则家族规则，例如 `Heavy Delving + Pickaxe` 拼成「重型探窟镐」，避免逐条硬编码
4. 运行时 `config/mia-zh/dict.json` 由 jar 内版本按内容指纹覆盖，用户改动写 `user.json`，存盘 2 秒热重载
5. `harvest.txt` 记录所有未命中的英文，`HandledScreenMixin` 会在打开容器时批量采集，用于兜住服务端配置之外的私有内容

## 数据来源

| 来源 | 用途 |
| --- | --- |
| github.com/MineInAbyss/server-config | 服务端真实物品名与 lore 原文，429 名 + 515 行 |
| 服务端资源包 `assets/minecraft/lang/zh_cn.json` | MIA 自己的译名，例如 Titanjaw 泰坦鳄、Eternal Fortune 不屈之花 |
| 原版 en_us.json 与 zh_cn.json | 2776 条原版名词官方译名 |
| 中文维基「来自深渊角色列表」 | 漫画官方译名，例如啼尸 槌嘴鸟 穿弹兽 永伪虫 毯毯鼠 |

## 待办

- 翻译 `tools/todo_lore.json` 里的 383 条 lore，填完并进 `mia_glossary.json` 的 lore 组
- 跨行 lore 是服务端拆行下发的，逐行翻会出现语序断裂，若要做整句重排需要改 `ItemStackMixin` 的整块处理
- NPC 对话（luxdialogues）与自定义 HUD 若走字体图渲染则经过不了文本组件，目前无解
- 服务端偶尔原样下发 `<emojy:...>` 标签与私用区图标，现已支持剥标签与剥图标后查表再补回

## 已知限制

- 服务端把句子拆成多行发送，本方案逐行替换，中文也会停在同样位置
- 含玩家名的聊天句子只有整句正则覆盖到的才会翻
- 词典是离线词表，没有联网翻译能力，模型不可用时依然按词表工作

## 客户端连不上服时

当前梯子节点只放行 TLS，Minecraft 的裸 TCP 25565 会被掐断

```bash
python3 tools/patch_flclash_rule.py     # 加 DOMAIN-SUFFIX,mineinabyss.com,DIRECT 并重启 FlClash
```

订阅更新会覆盖 profile，规则丢了重跑即可

## 安装

把 jar 放进实例的 `mods/` 目录，例如

```
/mnt/WindowsD/MC/.minecraft/versions/Mine In Abyss Modpack 1.4.2/mods/
```
