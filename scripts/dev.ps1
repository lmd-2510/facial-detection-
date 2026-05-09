param(
    [switch]$Build,
    [switch]$Seed
)

$ErrorActionPreference = "Stop"

$ComposeArgs = @("compose", "up", "-d")
if ($Build) {
    $ComposeArgs += "--build"
}

Write-Host "Starting DeepFace Access stack..." -ForegroundColor Cyan
docker @ComposeArgs

Write-Host ""
Write-Host "Stack is starting. Useful URLs:" -ForegroundColor Green
Write-Host "- Backend health: http://localhost:8000/health"
Write-Host "- Backend docs:   http://localhost:8000/docs"
Write-Host "- User app:       http://localhost:5173"
Write-Host "- Admin app:      http://localhost:5174"
Write-Host "- Nginx entry:    http://localhost:8080"
Write-Host "- Prometheus:     http://localhost:9090"

if ($Seed) {
    Write-Host ""
    Write-Host "Seeding demo users..." -ForegroundColor Cyan
    docker compose run --rm backend python -m app.db.seed
}
