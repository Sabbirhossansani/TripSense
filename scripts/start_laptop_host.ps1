<#
.SYNOPSIS
    Starts the local GPU/CPU TripSense FastAPI backend and exposes it over a free
    HTTPS Cloudflare Quick Tunnel for instant connection from the Vercel website.
#>

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "backend"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " TripSense Zero-Cost Laptop AI Host + Cloudflare Quick Tunnel" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "[WARNING] 'cloudflared' is not installed on PATH." -ForegroundColor Yellow
    Write-Host "Install it free in 10 seconds with:" -ForegroundColor Yellow
    Write-Host "  winget install --id Cloudflare.cloudflared -e" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting local-only FastAPI server on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
    Set-Location $BackendDir
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    exit 0
}

Write-Host "[1/2] Starting TripSense FastAPI + FairNet backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
$uvicornProc = Start-Process -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $BackendDir `
    -PassThru

Start-Sleep -Seconds 3

Write-Host "[2/2] Opening free HTTPS Cloudflare Tunnel (copy the https://*.trycloudflare.com URL)..." -ForegroundColor Green
Write-Host "Paste that URL into TripSense -> 'AI Engine -> Connect AI' on your Vercel site." -ForegroundColor Yellow
Write-Host ""

try {
    cloudflared tunnel --url http://127.0.0.1:8000
} finally {
    if ($uvicornProc -and -not $uvicornProc.HasExited) {
        Stop-Process -Id $uvicornProc.Id -Force
        Write-Host "Stopped local uvicorn server." -ForegroundColor DarkGray
    }
}
