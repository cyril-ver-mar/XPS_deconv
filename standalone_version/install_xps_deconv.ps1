# XPS-Deconv Windows bootstrapper (ASCII / PS 5.1 safe)
# Prefer running via: .\install_xps_deconv.bat

$ErrorActionPreference = "Stop"

$Repo = "cyril-ver-mar/XPS_deconv"
if ($env:XPS_DECONV_GITHUB_REPO) { $Repo = $env:XPS_DECONV_GITHUB_REPO }

$AppDirName = "XPS-Deconv"
if ($PSScriptRoot) { $ScriptDir = $PSScriptRoot } else { $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$Preserve = @("data", "exports", "venv", ".venv")

function Write-Info([string]$Msg) { Write-Host $Msg }

Write-Info ""
Write-Info "  ============================================================"
Write-Info "    XPS-Deconv - Bootstrap (download latest from GitHub)"
Write-Info "  ============================================================"
Write-Info ""
Write-Info "  WARNING"
Write-Info ""
Write-Info "  This script will download and install XPS-Deconv"
Write-Info "  INTO THE FOLDER WHERE THIS SCRIPT IS LOCATED:"
Write-Info ("    " + $ScriptDir)
Write-Info ""
Write-Info ("  Creates/updates folder: " + $AppDirName)
Write-Info "  Keeps if present: data, exports, venv"
Write-Info "  Needs network now; Python 3.11 later for install.bat"
Write-Info ""

$Confirm = Read-Host "  Type YES to continue (anything else cancels)"
if ($Confirm -ne "YES") {
    Write-Info ""
    Write-Info "  Cancelled."
    Write-Info ""
    exit 0
}

$Headers = @{
    "User-Agent" = "XPS-Deconv-bootstrap"
    "Accept" = "application/vnd.github+json"
}

Write-Info ""
Write-Info "  [1/4] Resolve latest GitHub Release..."
$ApiUrl = "https://api.github.com/repos/$Repo/releases/latest"
try {
    $Rel = Invoke-RestMethod -Uri $ApiUrl -Headers $Headers
} catch {
    Write-Info ""
    Write-Info "  ERROR: GitHub API failed."
    Write-Info ("  " + $_.Exception.Message)
    exit 1
}

$Zips = @()
foreach ($Asset in $Rel.assets) {
    if ($Asset.name -like "*.zip" -and $Asset.browser_download_url) {
        $Zips += $Asset
    }
}
if ($Zips.Count -eq 0) {
    Write-Info "  ERROR: No .zip on latest release."
    exit 1
}

$Preferred = $null
foreach ($Asset in $Zips) {
    if ($Asset.name -match "standalone") { $Preferred = $Asset; break }
}
if (-not $Preferred) {
    foreach ($Asset in $Zips) {
        if ($Asset.name -match "xps-deconv") { $Preferred = $Asset; break }
    }
}
if (-not $Preferred) { $Preferred = $Zips[0] }

Write-Info ("  OK Latest release: " + $Rel.tag_name)
Write-Info ("  OK Asset: " + $Preferred.name)

$Tmp = Join-Path $env:TEMP ("xps_deconv_boot_" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Tmp | Out-Null
$ZipPath = Join-Path $Tmp "pkg.zip"
$Extract = Join-Path $Tmp "extract"
$Hold = Join-Path $Tmp "preserve"
$Dest = Join-Path $ScriptDir $AppDirName

Write-Info ""
Write-Info "  [2/4] Download package..."
try {
    Invoke-WebRequest -Uri $Preferred.browser_download_url -OutFile $ZipPath -Headers @{ "User-Agent" = "XPS-Deconv-bootstrap" }
    Write-Info "  OK Downloaded"
} catch {
    Write-Info ("  ERROR download: " + $_.Exception.Message)
    Remove-Item -Path $Tmp -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Info ""
Write-Info ("  [3/4] Unpack into " + $Dest)
New-Item -ItemType Directory -Path $Extract | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $Extract -Force

$AppPy = $null
Get-ChildItem -Path $Extract -Recurse -Filter "app.py" | ForEach-Object {
    $VerCandidate = Join-Path $_.DirectoryName "VERSION"
    if ((-not $AppPy) -and (Test-Path $VerCandidate)) { $AppPy = $_ }
}
if (-not $AppPy) {
    Write-Info "  ERROR: zip has no app.py + VERSION"
    Remove-Item -Path $Tmp -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}
$Src = $AppPy.Directory.FullName

New-Item -ItemType Directory -Path $Hold | Out-Null
if (-not (Test-Path $Dest)) {
    New-Item -ItemType Directory -Path $Dest | Out-Null
}

foreach ($Name in $Preserve) {
    $P = Join-Path $Dest $Name
    if (Test-Path $P) {
        Move-Item -Path $P -Destination (Join-Path $Hold $Name) -Force
        Write-Info ("  OK Preserved " + $Name)
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
    Write-Info ("  OK VERSION " + $Ver)
}
Write-Info ("  OK Installed to " + $Dest)

Remove-Item -Path $Tmp -Recurse -Force -ErrorAction SilentlyContinue

Write-Info ""
Write-Info "  [4/4] Next steps"
Write-Info ""
Write-Info "  1. Open cmd or PowerShell"
Write-Info "  2. cd to app folder:"
Write-Info ("     cd /d " + $Dest)
Write-Info "  3. First time: install.bat"
Write-Info "  4. Start: run.bat"
Write-Info ""
Write-Info "  Browser: http://localhost:8501"
Write-Info ""
Write-Info "  OK Bootstrap finished."
Write-Info ""
