"""
sequencer.py — Séquenceur 16 pas → OSC pour Synthiker (design Octatrack).

Envoie des triggers OSC vers Pure Data (port 5005) à chaque tick.
Chaque tick = une double-croche (BPM / 4 en temps).

Usage :
    python sim/sequencer.py
    python sim/sequencer.py --bpm 128
"""

import argparse
import sys
import time

sys.path.insert(0, __file__.replace("/sim/sequencer.py", ""))

from sim.osc_bridge import make_pd_client, ADDR_SEQ_STEP, ADDR_SEQ_TRIG
from sim.presets.octatrack import PATTERNS, DEFAULT_BPM

# ---------------------------------------------------------------------------
# Pistes Octatrack : 4 percussions + 4 mélodiques
# ---------------------------------------------------------------------------
TRACK_NAMES = ["bd", "sd", "hat", "clap", "bass", "lead", "chord", "fx"]
TRACK_STEPS = [PATTERNS[name] for name in TRACK_NAMES]


def run_sequencer(bpm: int) -> None:
    """Boucle principale du séquenceur.

    Parcourt 16 steps en boucle, envoie un tick toutes les 60/(bpm*4) secondes
    (doubles-croches). Design Octatrack : 8 pistes (BD/SD/HH/CL + BASS/LEAD/CHORD/FX).
    """
    client = make_pd_client()
    step_duration = 60.0 / (bpm * 4)  # durée d'une double-croche en secondes
    step = 0

    print(f"[SEQ] Démarrage — BPM={bpm}, step_duration={step_duration:.4f}s")
    print(f"[SEQ] Pistes : {TRACK_NAMES}")
    print("[SEQ] Ctrl+C pour arrêter\n")

    try:
        while True:
            # Envoie le numéro du step courant
            client.send_message(ADDR_SEQ_STEP, step)

            # Envoie les triggers de chaque piste
            active_tracks = []
            for track_idx, steps in enumerate(TRACK_STEPS):
                trig = steps[step]
                client.send_message(ADDR_SEQ_TRIG.format(track_idx), trig)
                if trig:
                    active_tracks.append(TRACK_NAMES[track_idx])

            # Visualisation texte (barre de progression)
            bar = "".join(
                "█" if TRACK_STEPS[0][i] else "·"  # kick comme référence
                for i in range(16)
            )
            marker = list(bar)
            marker[step] = "▼"
            marker_str = " ".join(marker)
            active_str = ", ".join(active_tracks) if active_tracks else "—"
            line = f"[SEQ] Step {step:02d}/15  {marker_str}  active: {active_str:<20s}"
            if sys.stdout.isatty():
                print(f"\r{line}", end="", flush=True)
            else:
                print(line, flush=True)

            time.sleep(step_duration)
            step = (step + 1) % 16

    except KeyboardInterrupt:
        print("\n[SEQ] Arrêt propre.")


def main() -> None:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(description="Séquenceur 16 pas Synthiker Octatrack → OSC")
    parser.add_argument("--bpm", type=int, default=DEFAULT_BPM,
                        help=f"Tempo en BPM (défaut : {DEFAULT_BPM})")
    args = parser.parse_args()
    run_sequencer(args.bpm)


if __name__ == "__main__":
    main()
