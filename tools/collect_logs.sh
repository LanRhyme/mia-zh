#!/usr/bin/env bash
# 收集 mia-zh 模组日志，打包给维护者
# 用法: ./collect_logs.sh [游戏目录]
#   不给参数时依次尝试 ~/.minecraft 与当前目录

set -u

pick_dir() {
  if [ $# -ge 1 ] && [ -n "${1:-}" ]; then echo "$1"; return; fi
  for candidate in "$HOME/.minecraft" "$PWD"; do
    if [ -d "$candidate/config/mia-zh" ] || [ -f "$candidate/logs/latest.log" ]; then
      echo "$candidate"; return
    fi
  done
  echo "$HOME/.minecraft"
}

GAME_DIR="$(pick_dir "$@")"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${OUT_DIR:-$HOME/Desktop}"
[ -d "$OUT_DIR" ] || OUT_DIR="$HOME"
PKG_NAME="mia-zh-logs-$STAMP"
STAGE="$(mktemp -d)/$PKG_NAME"
mkdir -p "$STAGE"

echo "游戏目录: $GAME_DIR"

MIA_DIR="$GAME_DIR/config/mia-zh"
if [ -d "$MIA_DIR" ]; then
  for f in harvest.txt dict.json user.json config.json harvest.old.txt; do
    [ -f "$MIA_DIR/$f" ] && cp "$MIA_DIR/$f" "$STAGE/" && echo "  收集 config/mia-zh/$f"
  done
else
  echo "  未找到 config/mia-zh ，确认模组已加载并进过一次游戏"
fi

[ -f "$GAME_DIR/logs/latest.log" ] && cp "$GAME_DIR/logs/latest.log" "$STAGE/" && echo "  收集 logs/latest.log"

# 崩溃报告（有就带上）
if [ -d "$GAME_DIR/crash-reports" ]; then
  latest_crash="$(ls -t "$GAME_DIR"/crash-reports/*.txt 2>/dev/null | head -1)"
  [ -n "${latest_crash:-}" ] && cp "$latest_crash" "$STAGE/" && echo "  收集 $(basename "$latest_crash")"
fi

# 模组版本信息
{
  echo "game_dir: $GAME_DIR"
  echo "collected_at: $STAMP"
  echo "mod_jar: $(ls "$GAME_DIR"/mods/mia-zh-*.jar 2>/dev/null | xargs -r -n1 basename | tr '\n' ' ')"
  echo "os: $(uname -srm)"
} > "$STAGE/info.txt"

ARCHIVE="$OUT_DIR/$PKG_NAME.tar.gz"
tar -czf "$ARCHIVE" -C "$(dirname "$STAGE")" "$PKG_NAME"
rm -rf "$(dirname "$STAGE")"

echo
echo "打包完成: $ARCHIVE"
echo "harvest.txt 里是从未翻译过的英文，是维护者最需要的东西"
