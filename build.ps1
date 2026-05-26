# BAAS Pro Build Script
# Usage:
#   .\build.ps1                   incremental onedir (dev)
#   .\build.ps1 -Clean            full rebuild
#   .\build.ps1 -Release          incremental onefile
#   .\build.ps1 -Release -Clean   full rebuild onefile (distribution)

param(
    [switch]$Clean,
    [switch]$Release
)

$ErrorActionPreference = "Stop"

$mode = if ($Release) { "onefile" } else { "onedir" }
$buildLabel = if ($Clean) { "full rebuild" } else { "incremental" }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BAAS Pro Build  |  $mode  |  $buildLabel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$distPath = Join-Path $root "dist"
$buildPath = Join-Path $root "build"
$specFile = Join-Path $root "build.spec"

if ($Clean) {
    if (Test-Path $distPath) {
        Write-Host "[1/3] Cleaning dist..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $distPath -ErrorAction SilentlyContinue
    }
    if (Test-Path $buildPath) {
        Write-Host "[1/3] Cleaning build cache..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $buildPath
    }
    Write-Host ""
} else {
    Write-Host "[1/3] Skipping clean (keeping cache)" -ForegroundColor Yellow
    Write-Host ""
}

$env:BAAS_ONEFILE = if ($Release) { "1" } else { "0" }

Write-Host "[2/3] Running PyInstaller ($mode)..." -ForegroundColor Yellow
$python = "D:\Python311\python.exe"
$sw = [Diagnostics.Stopwatch]::StartNew()
$proc = Start-Process -FilePath $python `
    -ArgumentList "-m", "PyInstaller", "--distpath", $distPath, "--workpath", $buildPath, "--noconfirm", $specFile `
    -NoNewWindow -Wait -PassThru
$sw.Stop()

if ($proc.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    exit 1
}

if ($Release) {
    $exePath = Join-Path $distPath "baas.exe"
} else {
    $exePath = Join-Path (Join-Path $distPath "baas") "baas.exe"
}

if (Test-Path $exePath) {
    $sizeMB = if ($Release) {
        [math]::Round((Get-Item $exePath).Length / 1MB, 1)
    } else {
        [math]::Round(((Get-ChildItem -Recurse (Join-Path $distPath "baas") -File | Measure-Object Length -Sum).Sum) / 1MB, 1)
    }
    Write-Host ""
    Write-Host "[3/3] Done!  $([math]::Round($sw.Elapsed.TotalSeconds, 0))s  |  $sizeMB MB" -ForegroundColor Green
    Write-Host "      $exePath" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Output not found: $exePath" -ForegroundColor Red
    exit 1
}
