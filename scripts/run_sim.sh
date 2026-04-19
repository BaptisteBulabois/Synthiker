#!/usr/bin/env bash
# run_sim.sh — Lance toute la stack de simulation Synthiker
# Usage : bash scripts/run_sim.sh
set -euo pipefail

# ---------------------------------------------------------------------------
# Vérifications préliminaires
# ---------------------------------------------------------------------------

# Vérifier que Pure Data est dans le PATH
command -v pd >/dev/null 2>&1 || {
    echo "❌ 'pd' non trouvé dans PATH."
    echo "   macOS : brew install --cask pd"
    echo "   Linux : sudo apt install puredata"
    echo "   Windows/autre : https://puredata.info/downloads"
    exit 1
}

# Vérifier que le venv est activé
[ -z "${VIRTUAL_ENV:-}" ] && echo "⚠️  Venv non activé — pensez à 'source venv/bin/activate'"

# Vérifier que le patch Pd existe
[ -f "pd_patches/synth_main.pd" ] || {
    echo "❌ pd_patches/synth_main.pd introuvable. Exécutez ce script depuis la racine du repo."
    exit 1
}

echo "🎛️  Synthiker — Démarrage de la simulation PC"
echo "============================================="

# ---------------------------------------------------------------------------
# Lancer Pure Data en arrière-plan
# ---------------------------------------------------------------------------
echo "🎵 Lancement Pure Data (port OSC 5005)..."
pd -nogui -open pd_patches/synth_main.pd &
PID_PD=$!
echo "   PID Pure Data : $PID_PD"

# Laisser Pd s'initialiser avant d'envoyer des OSC
sleep 2

# ---------------------------------------------------------------------------
# Lancer les composants Python
# ---------------------------------------------------------------------------
echo "🖥️  Lancement fake_panel (PyGame)..."
python sim/fake_panel.py &
PID_PANEL=$!
echo "   PID fake_panel : $PID_PANEL"

echo "🥁 Lancement séquenceur (BPM=120)..."
python sim/sequencer.py --bpm 120 &
PID_SEQ=$!
echo "   PID séquenceur : $PID_SEQ"

echo ""
echo "✅ Simulation démarrée !"
echo "   • Fenêtre PyGame : molette=encodeur, Q/W=changer encodeur, 1-8=boutons"
echo "   • Ctrl+C pour tout arrêter"
echo ""

# ---------------------------------------------------------------------------
# Nettoyage à la sortie (Ctrl+C ou fin des process)
# ---------------------------------------------------------------------------
cleanup() {
    echo ""
    echo "🛑 Arrêt de la simulation..."
    kill "$PID_PD"     2>/dev/null || true
    kill "$PID_PANEL"  2>/dev/null || true
    kill "$PID_SEQ"    2>/dev/null || true
    echo "   Tous les process arrêtés."
}

trap cleanup EXIT INT TERM

# Attendre que tous les process se terminent
wait
