# 收集 mia-zh 模组日志并打包到桌面
#
# 用法（在 PowerShell 里）:
#   powershell -ExecutionPolicy Bypass -File collect_logs.ps1
#   powershell -ExecutionPolicy Bypass -File collect_logs.ps1 -GameDir "D:\MC\.minecraft"
#
# 不给 -GameDir 时依次尝试 %APPDATA%\.minecraft 与 HMCL 常见目录

param(
    [string]$GameDir = ""
)

$ErrorActionPreference = "SilentlyContinue"

function Test-GameDir([string]$dir) {
    if ([string]::IsNullOrWhiteSpace($dir)) { return $false }
    return (Test-Path (Join-Path $dir "config\mia-zh")) -or (Test-Path (Join-Path $dir "logs\latest.log"))
}

if (-not (Test-GameDir $GameDir)) {
    $candidates = @(
        (Join-Path $env:APPDATA ".minecraft"),
        (Join-Path $env:USERPROFILE ".minecraft"),
        (Join-Path $env:APPDATA ".minecraft\versions\$((Get-ChildItem (Join-Path $env:APPDATA '.minecraft\versions') -Directory | Select-Object -First 1).Name)")
    )
    foreach ($c in $candidates) {
        if (Test-GameDir $c) { $GameDir = $c; break }
    }
}

if (-not (Test-GameDir $GameDir)) {
    Write-Host "没找到游戏目录，请用 -GameDir 指定 .minecraft 的路径" -ForegroundColor Yellow
    exit 1
}

Write-Host "游戏目录: $GameDir"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$name = "mia-zh-logs-$stamp"
$stage = Join-Path $env:TEMP $name
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$miaDir = Join-Path $GameDir "config\mia-zh"
if (Test-Path $miaDir) {
    foreach ($f in @("harvest.txt", "dict.json", "user.json", "config.json", "harvest.old.txt")) {
        $src = Join-Path $miaDir $f
        if (Test-Path $src) {
            Copy-Item $src $stage
            Write-Host "  收集 config\mia-zh\$f"
        }
    }
} else {
    Write-Host "  未找到 config\mia-zh，确认模组已加载且进过一次游戏" -ForegroundColor Yellow
}

$log = Join-Path $GameDir "logs\latest.log"
if (Test-Path $log) { Copy-Item $log $stage; Write-Host "  收集 logs\latest.log" }

$crashDir = Join-Path $GameDir "crash-reports"
if (Test-Path $crashDir) {
    $crash = Get-ChildItem $crashDir -Filter *.txt | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($crash) { Copy-Item $crash.FullName $stage; Write-Host "  收集 $($crash.Name)" }
}

$jar = Get-ChildItem (Join-Path $GameDir "mods") -Filter "mia-zh-*.jar" | Select-Object -First 1
@(
    "game_dir: $GameDir",
    "collected_at: $stamp",
    "mod_jar: $($jar.Name)",
    "windows: $([System.Environment]::OSVersion.VersionString)"
) | Set-Content (Join-Path $stage "info.txt") -Encoding UTF8

$desktop = [Environment]::GetFolderPath("Desktop")
if (-not (Test-Path $desktop)) { $desktop = $env:TEMP }
$archive = Join-Path $desktop "$name.zip"
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $archive -Force
Remove-Item -Recurse -Force $stage

Write-Host ""
Write-Host "打包完成: $archive" -ForegroundColor Green
Write-Host "harvest.txt 里是从未翻译过的英文，是维护者最需要的东西"
