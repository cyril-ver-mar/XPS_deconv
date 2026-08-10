# XPS-Deconv one-file bootstrapper (Windows PowerShell)
# Downloads the latest GitHub Release zip into the folder that contains THIS script.
# Called by install_xps_deconv.bat or run directly:
#   powershell -ExecutionPolicy Bypass -File .\install_xps_deconv.ps1

$ErrorActionPreference = "Stop"

$Repo = if ($env:XPS_DECONV_GITHUB_REPO) { $env:XPS_DECONV_GITHUB_REPO } else { "cyril-ver-mar/XPS_deconv" }
$AppDirName = "XPS-Deconv"
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Preserve = @("data", "exports", "venv", ".venv")

Write-Host ""
Write-Host "  ============================================================"
Write-Host "    XPS-Deconv  —  Bootstrap (download latest from GitHub)"
Write-Host "  ============================================================"
Write-Host ""
Write-Host "  WARNING / ПРЕДУПРЕЖДЕНИЕ"
Write-Host ""
Write-Host "  This script will download and install XPS-Deconv"
Write-Host "  INTO THE FOLDER WHERE THIS SCRIPT IS LOCATED:"
Write-Host ""
Write-Host "    $ScriptDir"
Write-Host ""
Write-Host "  Этот скрипт скачает и установит XPS-Deconv"
Write-Host "  В ТУ ЖЕ ПАПКУ, ГДЕ ЛЕЖИТ ЭТОТ ФАЙЛ:"
Write-Host ""
Write-Host "    $ScriptDir"
Write-Host ""
Write-Host "  - Creates / updates:  $AppDirName\"
Write-Host "  - Keeps (if present): data\, exports\, venv\"
Write-Host "  - Needs: network + Python 3.11 later for install.bat"
Write-Host ""

$Confirm = Read-Host "  Type YES to continue (anything else cancels)"
if ($Confirm -ne "YES") {
    Write-Host ""
    Write-Host "  Cancelled. Move this script to the folder where you want the app, then run again."
    Write-Host "  Отменено. Переложите скрипт в нужную папку и запустите снова."
    Write-Host ""
    exit 0
}

$Headers = @{
    "User-Agent" = "XPS-Deconv-bootstrap"
    "Accept"     = "application/vnd.github+json"
}

Write-Host ""
Write-Host "  [1/4] Resolve latest GitHub Release..."
try {
    $Rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -Headers $Headers
} catch {
    Write-Host ""
    Write-Host "  ERROR: GitHub API failed."
    Write-Host "  Check https://github.com/$Repo/releases"
    Write-Host "  $($_.Exception.Message)"
    exit 1
}

$Zips = @($Rel.assets | Where-Object { $_.name -match '\.zip$' -and $_.browser_download_url })
if (-not $Zips -or $Zips.Count -eq 0) {
    Write-Host ""
    Write-Host "  ERROR: No .zip asset on the latest release."
    Write-Host "  Attach XPS-Deconv-standalone-*.zip to the GitHub Release."
    exit 1
}

$Preferred = $Zips | Where-Object { $_.name -match 'standalone' } | Select-Object -First 1
if (-not $Preferred) {
    $Preferred = $Zips | Where-Object { $_.name -match 'xps-deconv' } | Select-Object -First 1
}
if (-not $Preferred) {
    $Preferred = $Zips[0]
}

Write-Host "  OK Latest release: $($Rel.tag_name)"
Write-Host "  OK Asset: $($Preferred.name)"

$Tmp = Join-Path $env:TEMP ("xps_deconv_boot_" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Tmp | Out-Null
try {
    Write-Host ""
    Write-Host "  [2/4] Download package..."
    $ZipPath = Join-Path $Tmp "pkg.zip"
    Invoke-WebRequest -Uri $Preferred.browser_download_url -OutFile $ZipPath -Headers @{ "User-Agent" = "XPS-Deconv-bootstrap" }
    Write-Host "  OK Downloaded"

    Write-Host ""
    $Dest = Join-Path $ScriptDir $AppDirName
    Write-Host "  [3/4] Unpack into $Dest ..."
    $Extract = Join-Path $Tmp "extract"
    New-Item -ItemType Directory -Path $Extract | Out-Null
    Expand-Archive -Path $ZipPath -DestinationPath $Extract -Force

    $AppPy = Get-ChildItem -Path $Extract -Recurse -Filter "app.py" |
        Where-Object { Test-Path (Join-Path $_.DirectoryName "VERSION") } |
        Select-Object -First 1
    if (-not $AppPy) {
        throw "Zip does not contain app.py + VERSION"
    }
    $Src = $AppPy.Directory.FullName

    $Hold = Join-Path $Tmp "preserve"
    New-Item -ItemType Directory -Path $Hold | Out-Null
    if (-not (Test-Path $Dest)) {
        New-Item -ItemType Directory -Path $Dest | Out-Null
    }

    foreach ($Name in $Preserve) {
        $P = Join-Path $Dest $Name
        if (Test-Path $P) {
            Move-Item -Path $P -Destination (Join-Path $Hold $Name) -Force
            Write-Host "  OK Preserved $Name"
        }
    }

    Get-ChildItem -Path $Dest -Force | Remove-Item -Recurse -Force
    Copy-Item -Path (Join-Path $Src "*") -Destination $Dest -Recurse -Force

    foreach ($Name in $Preserve) {
        $H = Join-Path $Hold $Name
        if (Test-Path $H) {
            $Target = Join-Path $Dest $Name
            if (Test-Path $Target) { Remove-Item -Path $Target -Recurse -Force }
            Move-Item -Path $H -Destination $Target -Force
        }
    }

    $VerFile = Join-Path $Dest "VERSION"
    if (Test-Path $VerFile) {
        $Ver = (Get-Content $VerFile -TotalCount 1).Trim()
        Write-Host "  OK VERSION $Ver"
    }
    Write-Host "  OK Installed to $Dest"

    Write-Host ""
    Write-Host "  [4/4] Next steps"
    Write-Host ""
    Write-Host "  How to finish setup and run"
    Write-Host ""
    Write-Host "  1. Open Command Prompt or PowerShell"
    Write-Host "  2. Go to the app folder:"
    Write-Host "     cd /d `"$Dest`""
    Write-Host "  3. First time only — install Python deps:"
    Write-Host "     install.bat"
    Write-Host "  4. Start the app:"
    Write-Host "     run.bat"
    Write-Host ""
    Write-Host "  Browser: http://localhost:8501  (or http://127.0.0.1:8501)"
    Write-Host ""
    Write-Host "  Как запустить:"
    Write-Host "  1. Откройте cmd"
    Write-Host "  2. cd в папку приложения (команда выше)"
    Write-Host "  3. install.bat   (один раз)"
    Write-Host "  4. run.bat"
    Write-Host ""
    Write-Host "  OK Bootstrap finished."
    Write-Host ""
}
finally {
    if (Test-Path $Tmp) {
        Remove-Item -Path $Tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
