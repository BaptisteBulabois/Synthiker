"""
design_selector.py — Lanceur de session Synthiker Octatrack.

Lance le séquenceur 16 pas avec les patterns et le BPM adaptés au design Octatrack
et affiche le patch Pure Data à ouvrir.

Patterns disponibles :
  default  — Pattern 4/4 standard (grosse caisse sur les temps, basse pulsée)
  live     — Syncopé, style performance Octatrack
  scene_b  — Dense, tous les éléments actifs (typique Scène B)

Usage :
    python sim/design_selector.py
    python sim/design_selector.py --bpm 128
    python sim/design_selector.py --pattern live
    python sim/design_selector.py --list
"""

import argparse
import sys
import time

sys.path.insert(0, __file__.replace("/sim/design_selector.py", ""))

from sim.osc_bridge import make_pd_client, make_oled_client, ADDR_ENC, ADDR_SEQ_STEP, ADDR_SEQ_TRIG
import sim.presets.octatrack as _octatrack

DESIGN_LABEL = "Elektron Octatrack"
DESIGN_PATCH = "pd_patches/synth_octatrack.pd"
TRACK_NAMES = ["bd", "sd", "hat", "clap", "bass", "lead", "chord", "fx"]

_PATTERNS: dict[str, dict] = {
    "default": _octatrack.PATTERNS,
    "live":    _octatrack.PATTERNS_LIVE,
    "scene_b": _octatrack.PATTERNS_SCENE_B,
}


def list_patterns() -> None:
    """Affiche les patterns disponibles."""
    print("\n╔══════════════════════════════════════════════╗")
    print("║      Synthiker — Octatrack  Patterns         ║")
    print("╠══════════════════════════════════════════════╣")
    for name in _PATTERNS:
        print(f"║  {name:<42} ║")
    print(f"║  Patch : {DESIGN_PATCH:<36} ║")
    print(f"║  BPM   : {_octatrack.DEFAULT_BPM:<36} ║")
    print("╚══════════════════════════════════════════════╝\n")


def send_encoder_defaults(pd_client, oled_client, defaults: list[int]) -> None:
    """Envoie les valeurs d'encodeurs par défaut via OSC."""
    for idx, val in enumerate(defaults):
        pd_client.send_message(ADDR_ENC.format(idx), val)
        oled_client.send_message(ADDR_ENC.format(idx), val)
    print(f"[DESIGN] Encodeurs initialisés ({len(defaults)} valeurs envoyées)")


def run_sequencer(patterns: dict[str, list[int]], bpm: int, track_names: list[str]) -> None:
    """Boucle séquenceur 16 pas avec les patterns Octatrack."""
    pd_client = make_pd_client()
    step_duration = 60.0 / (bpm * 4)
    track_steps = [patterns.get(name, [0] * 16) for name in track_names]
    step = 0

    print(f"[SEQ] BPM={bpm}  step={step_duration:.4f}s  pistes={track_names}")
    print("[SEQ] Ctrl+C pour arrêter\n")

    try:
        while True:
            pd_client.send_message(ADDR_SEQ_STEP, step)

            active = []
            for track_idx, steps in enumerate(track_steps):
                trig = steps[step]
                pd_client.send_message(ADDR_SEQ_TRIG.format(track_idx), trig)
                if trig:
                    active.append(track_names[track_idx])

            bar = "".join("█" if track_steps[0][i] else "·" for i in range(16))
            marker = list(bar)
            marker[step] = "▼"
            active_str = ", ".join(active) if active else "—"
            line = f"[SEQ] Step {step:02d}/15  {' '.join(marker)}  {active_str:<24}"
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
    parser = argparse.ArgumentParser(
        description="Synthiker Octatrack — lance le séquenceur 8 pistes"
    )
    parser.add_argument(
        "--pattern", choices=list(_PATTERNS.keys()), default="default",
        help="Pattern à charger (défaut : default)",
    )
    parser.add_argument(
        "--bpm", type=int, default=None,
        help=f"Tempo en BPM (défaut : {_octatrack.DEFAULT_BPM})",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Liste les patterns disponibles, puis quitte",
    )
    parser.add_argument(
        "--no-seq", action="store_true",
        help="N'initialise que les encodeurs sans démarrer le séquenceur",
    )
    args = parser.parse_args()

    if args.list:
        list_patterns()
        return

    bpm = args.bpm or _octatrack.DEFAULT_BPM
    patterns = _PATTERNS[args.pattern]

    print(f"\n╔══════════════════════════════════════════════╗")
    print(f"║  Design  : {DESIGN_LABEL:<33}║")
    print(f"║  Pattern : {args.pattern:<33}║")
    print(f"║  BPM     : {bpm:<33}║")
    print(f"║  Patch Pd: {DESIGN_PATCH:<33}║")
    print(f"╚══════════════════════════════════════════════╝")
    print(f"\n  → Ouvre le patch dans Pure Data :")
    print(f"    pd {DESIGN_PATCH}\n")

    print("  ── Mode Octatrack ──────────────────────────────")
    print("  Scènes A/B : utilise fake_panel.py --octatrack")
    print("    P1 → Scène A   P2 → Scène B   P3 → Morph A↔B")
    print("    ENC 11 (M3)   → crossfader /oct/scene")
    print("    1-8 + molette → P-lock sur le step courant")
    print("  ────────────────────────────────────────────────\n")

    pd_client = make_pd_client()
    oled_client = make_oled_client()
    send_encoder_defaults(pd_client, oled_client, _octatrack.ENCODER_DEFAULTS_A)

    if args.no_seq:
        print("[DESIGN] Mode --no-seq : encodeurs initialisés, séquenceur non démarré.")
        return

    run_sequencer(patterns, bpm, TRACK_NAMES)


if __name__ == "__main__":
    main()
