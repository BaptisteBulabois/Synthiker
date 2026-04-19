# docker_run.ps1 — Lanceur PowerShell pour Synthiker (Docker hybride, Windows)
# Usage : .\scripts\docker_run.ps1

Write-Host ""
Write-Host "🎛️  Synthiker — Lancement du backend Docker (approche hybride)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Avant de continuer, assurez-vous que :"
Write-Host "   1. Pure Data est lancé et le DSP est ACTIVÉ"
Write-Host "      → pd pd_patches\synth_main.pd  (puis Media → DSP On)"
Write-Host "   2. fake_panel.py tourne sur l'hôte (optionnel) :"
Write-Host "      → .\venv\Scripts\Activate.ps1 && python sim\fake_panel.py"
Write-Host ""
Write-Host "Appuyez sur une touche pour démarrer le container..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

# Activer le mode tracker si la variable est définie
if ($env:ENABLE_TRACKER -eq "1") {
    Write-Host "🎼 Mode tracker activé (ENABLE_TRACKER=1)" -ForegroundColor Green
}

Write-Host "🐳 Démarrage du container backend..." -ForegroundColor Green
docker compose up --build

Write-Host ""
Write-Host "✅ Container arrêté. Pour tout nettoyer : docker compose down" -ForegroundColor Green
