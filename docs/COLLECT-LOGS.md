# 让别人把日志发回来

模组的汉化靠离线词典

词典里没有的英文会被记录到 `config/mia-zh/harvest.txt`

维护者只需要这份文件，加上 `logs/latest.log` 用来排查模组是否正常加载

## 一键脚本

仓库 `tools/` 下已带脚本，会把需要的东西打包到桌面

Windows

```powershell
powershell -ExecutionPolicy Bypass -File tools\collect_logs.ps1
powershell -ExecutionPolicy Bypass -File tools\collect_logs.ps1 -GameDir "D:\MC\.minecraft"
```

Linux / macOS

```bash
bash tools/collect_logs.sh
bash tools/collect_logs.sh "/path/to/.minecraft"
```

产物是 `mia-zh-logs-<时间>.zip` 或 `.tar.gz`，直接发过来即可

## 手动方式

不想跑脚本就照抄两个路径里的文件

| 文件 | 作用 |
| --- | --- |
| `<游戏目录>/config/mia-zh/harvest.txt` | 未翻译英文，最重要 |
| `<游戏目录>/logs/latest.log` | 启动日志，看模组有没有加载 |
| `<游戏目录>/config/mia-zh/user.json` | 可选，自定义覆盖表 |
| `<游戏目录>/crash-reports/*.txt` | 可选，崩溃报告 |

把 `<游戏目录>` 换成实际路径

## 游戏目录在哪

| 启动器 | 常见路径 |
| --- | --- |
| 官方启动器 Windows | `%APPDATA%\.minecraft` |
| HMCL / PCL2 整合包 | 启动器里选中实例，点开实例文件夹，找 `.minecraft` 或版本目录 |
| 多版本目录 | `versions/<整合包名>/` 里同样有 `config` 与 `logs` |
| Linux 官方启动器 | `~/.minecraft` |

如果 `config/mia-zh` 不存在，说明模组没加载或者还没进过游戏

## 采集前要做的事

1. 进一次服务器
2. 打开背包、箱子、末影箱、商店、公会仓库等界面，让模组把物品名与 lore 扫一遍
3. 把鼠标悬停在还没汉化的物品上看一圈
4. 玩十到二十分钟，遇到英文界面或提示就点开看看
5. 退出游戏后再打包，这样日志最完整

## 隐私提醒

- `harvest.txt` 只包含界面与物品文本，不含聊天与玩家名，发出来最安全
- `logs/latest.log` 可能含聊天记录、玩家昵称、服务器地址
- 只想给翻译素材就单独发 `harvest.txt`
