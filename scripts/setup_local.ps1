# RegIntel local setup (Windows)
# Usage: .\scripts\setup_local.ps1 [-StartApp]

param(
    [switch]$StartApp
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> Starting Docker services..." -ForegroundColor Cyan
docker compose up -d postgres neo4j qdrant redis

Write-Host "==> Waiting for services..." -ForegroundColor Cyan
python scripts/wait_for_services.py

Write-Host "==> Running migrations..." -ForegroundColor Cyan
alembic -c services/api/alembic.ini upgrade head
python scripts/run_graph_migrations.py
python services/retrieval/migrations/setup_collection.py

Write-Host "==> Seeding demo tenant..." -ForegroundColor Cyan
python scripts/seed_demo.py

Write-Host "==> Embedding search corpus..." -ForegroundColor Cyan
python scripts/embed_sources.py --sources reference sec_edgar --sec-limit 5

Write-Host ""
Write-Host "RegIntel is ready." -ForegroundColor Green
Write-Host "  Web:    http://localhost:3000"
Write-Host "  API:    http://localhost:8000/docs"
Write-Host "  Login:  admin@regintel.dev / RegIntel-Demo-2025!"
Write-Host ""

if ($StartApp) {
    Write-Host "Starting API and web in new windows..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root'; uvicorn services.api.main:app --host 0.0.0.0 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\web'; npm run dev"
} else {
    Write-Host "Next: make run-api  (terminal 1)  &&  make run-web  (terminal 2)"
}
