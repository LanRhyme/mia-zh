mia-zh 0.7.0 交接包

1) mia-zh-0.7.0.jar
   直接放进 Minecraft 1.21.11 Fabric 实例的 mods 目录即可
   首次启动会在 config/mia-zh/ 生成词典与 harvest.txt

2) mia-zh-0.7.0-src.zip
   完整源码，解压后：
     python3 tools/build_dict.py   # 生成词典
     ./gradlew build               # 需要 JDK 21
   详细说明见 docs/HANDOFF.md

3) 当前进度
   物品名 429/429 100%
   lore   132/515 25%，未翻的 383 条在 tools/todo_lore.json

4) 连不上服的话
   python3 tools/patch_flclash_rule.py
