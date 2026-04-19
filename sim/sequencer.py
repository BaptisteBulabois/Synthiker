"""
sequencer.py — Séquenceur 16 pas → OSC pour Synthiker.

Envoie des triggers OSC vers Pure Data (port 5005) à chaque tick.
Chaque tick = une double-croche (BPM / 4 en temps).

Usage :
    python sim/sequencer.py --bpm 120
"""

import argparse
import sys
import time

sys.path.insert(0, __file__.replace("/sim/sequencer.py", ""))

from sim.osc_bridge import make_pd_client, ADDR_SEQ_STEP, ADDR_SEQ_TRIG

# ---------------------------------------------------------------------------
# Patterns 16 pas par défaut (4 pistes)
# ---------------------------------------------------------------------------
PATTERNS = {
    "kick":  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
    "hat":   [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
    "perc":  [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
}
TRACK_NAMES = list(PATTERNS.keys())
TRACK_STEPS = [PATTERNS[name] for name in TRACK_NAMES]


def run_sequencer(bpm: int) -> None:
    """Boucle principale du séquenceur.

    Parcourt 16 steps en boucle, envoie un tick toutes les 60/(bpm*4) secondes
    (doubles-croches).
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
            print(f"\r[SEQ] Step {step:02d}/15  {' '.join(marker)}  "
                  f"  active: {active_tracks if active_tracks else '—':20s}",
                  end="", flush=True)

            time.sleep(step_duration)
            step = (step + 1) % 16

    except KeyboardInterrupt:
        print("\n[SEQ] Arrêt propre.")


def main() -> None:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(description="Séquenceur 16 pas Synthiker → OSC")
    parser.add_argument("--bpm", type=int, default=120,
                        help="Tempo en BPM (défaut : 120)")
    args = parser.parse_args()
    run_sequencer(args.bpm)


if __name__ == "__main__":
    main()
