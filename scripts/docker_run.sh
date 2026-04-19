#!/usr/bin/env bash
# docker_run.sh — Lanceur Bash pour Synthiker (Docker hybride)
# Usage : bash scripts/docker_run.sh
set -euo pipefail

echo ""
echo "🎛️  Synthiker — Lancement du backend Docker (approche hybride)"
echo "================================================================"
echo ""
echo "⚠️  Avant de continuer, assurez-vous que :"
echo "   1. Pure Data est lancé et le DSP est ACTIVÉ"
echo "      → pd pd_patches/synth_main.pd  (puis Media → DSP On)"
echo "   2. fake_panel.py tourne sur l'hôte (optionnel) :"
echo "      → source venv/bin/activate && python sim/fake_panel.py"
echo ""
echo "Appuyez sur Entrée pour démarrer le container..."
read -r

# Activer le mode tracker si la variable est définie
if [ "${ENABLE_TRACKER:-0}" = "1" ]; then
    echo "🎼 Mode tracker activé (ENABLE_TRACKER=1)"
fi

echo "🐳 Démarrage du container backend..."
docker compose up --build

echo ""
echo "✅ Container arrêté. Pour tout nettoyer : docker compose down"
