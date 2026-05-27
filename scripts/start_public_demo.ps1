param(
    [int]$Port = 8501,
    [string]$AppFile = "app.py"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Get-Command streamlit -ErrorAction SilentlyContinue)) {
    throw "streamlit command not found. Activate your virtual environment and install requirements first."
}

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    throw "cloudflared command not found. Install it first (winget install Cloudflare.cloudflared)."
}

$streamlitRunning = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if (-not $streamlitRunning) {
    $streamlitArgs = "-NoProfile -Command `"streamlit run `"$AppFile`" --server.headless true --server.port $Port`""
    Start-Process -FilePath "powershell" -ArgumentList $streamlitArgs -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 6
}

Write-Host "Starting public tunnel for http://localhost:$Port ..."
Write-Host "Press Ctrl+C to stop tunnel."

cloudflared tunnel --url "http://localhost:$Port"
