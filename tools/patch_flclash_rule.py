#!/usr/bin/env python3
"""给 FlClash 当前订阅补一条 mineinabyss.com 走直连的规则，然后重启 FlClash

背景：当前节点只放行 TLS，Minecraft 的裸 TCP 25565 会被掐，表现为服务器列表「连接中断」
订阅更新会覆盖 profile，所以更新后用本脚本重打一次即可（幂等）

用法：
  python3 tools/patch_flclash_rule.py            # 写入规则并重启 FlClash
  python3 tools/patch_flclash_rule.py --dry-run  # 只看会做什么
"""

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DATA = Path.home() / ".local/share/com.follow.clash"
PREFS = DATA / "shared_preferences.json"
BACKUP_ROOT = Path.home() / "tmp"

RULES = [
    "'DOMAIN-SUFFIX,mineinabyss.com,DIRECT'",
    "'IP-CIDR,144.76.219.79/32,DIRECT,no-resolve'",
]


def active_profile() -> Path:
    cfg = json.loads(json.loads(PREFS.read_text(encoding="utf-8"))["flutter.config"])
    pid = cfg["currentProfileId"]
    return DATA / "profiles" / f"{pid}.yaml"


def patch(profile: Path, dry: bool) -> bool:
    lines = profile.read_text(encoding="utf-8").split("\n")
    body = "\n".join(lines)
    missing = [r for r in RULES if r.strip("'") not in body]
    if not missing:
        print(f"规则已在 {profile.name} 中，无需改动")
        return False
    if dry:
        print(f"[dry-run] 将向 {profile.name} 的 rules: 顶部插入 {len(missing)} 条：")
        for r in missing:
            print("   ", r)
        return False

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = BACKUP_ROOT / f"flclash-backup-{stamp}"
    bk.mkdir(parents=True, exist_ok=True)
    for f in (DATA / "config.yaml", profile, PREFS):
        if f.exists():
            shutil.copy2(f, bk / f.name)
    print(f"备份 -> {bk}")

    out = []
    done = False
    for line in lines:
        out.append(line)
        if not done and line.strip() == "rules:":
            out.extend("    - " + r for r in RULES)
            done = True
    if not done:
        sys.exit("profile 里没有 rules: 段，放弃")
    profile.write_text("\n".join(out), encoding="utf-8")
    print(f"已插入 {len(RULES)} 条规则 -> {profile.name}")
    return True


def restart_flclash() -> None:
    for name in ("FlClash", "FlClashCore"):
        subprocess.run(["pkill", "-x", name], check=False)
    time.sleep(2)
    subprocess.Popen(
        ["/usr/lib/flclash/FlClash"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print("FlClash 已重启，等 10 秒让它把规则渲染进 config.yaml")
    time.sleep(10)


def verify() -> int:
    cfg = DATA / "config.yaml"
    text = cfg.read_text(encoding="utf-8") if cfg.exists() else ""
    ok = "mineinabyss.com" in text
    print("生成配置含规则:", "是" if ok else "否")
    ps = subprocess.run(["pgrep", "-x", "FlClash"], capture_output=True, text=True)
    print("FlClash 进程:", "运行中" if ps.stdout.strip() else "未运行")
    return 0 if ok else 1


def main() -> None:
    dry = "--dry-run" in sys.argv
    profile = active_profile()
    print(f"活动订阅: {profile}")
    if patch(profile, dry):
        restart_flclash()
    if not dry:
        sys.exit(verify())


if __name__ == "__main__":
    main()
