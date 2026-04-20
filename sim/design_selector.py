"""
design_selector.py — Sélecteur de design Synthiker.

Lance le séquenceur 16 pas avec les patterns et le BPM adaptés au design choisi,
et affiche le patch Pure Data à ouvrir.

Designs disponibles :
  tr808    — Roland TR-808  (kick, snare, hi-hat, cowbell)
  elektron — Elektron / Digitakt  (kick FM, snare snap, hat métallique, clap)
  tb303    — Roland TB-303 Acid Bass  (basse acid monophonique)

Usage :
    python sim/design_selector.py --design tr808 --bpm 120
    python sim/design_selector.py --design elektron
    python sim/design_selector.py --design tb303 --pattern acid8
    python sim/design_selector.py --list
"""

import argparse
import sys
import time

sys.path.insert(0, __file__.replace("/sim/design_selector.py", ""))

from sim.osc_bridge import make_pd_client, make_oled_client, ADDR_ENC, ADDR_SEQ_STEP, ADDR_SEQ_TRIG
from sim.presets import DESIGNS
import sim.presets.tr808 as _tr808
import sim.presets.elektron as _elektron
import sim.presets.tb303 as _tb303
import sim.presets.octatrack as _octatrack

# Patterns alternatifs accessibles par nom
_EXTRA_PATTERNS: dict[str, dict] = {
    "tr808":    {
        "default":  _tr808.PATTERNS,
        "boombap":  _tr808.PATTERNS_BOOMBAP,
        "shuffle":  _tr808.PATTERNS_SHUFFLE,
    },
    "elektron": {
        "default":  _elektron.PATTERNS,
        "minimal":  _elektron.PATTERNS_MINIMAL,
        "poly":     _elektron.PATTERNS_POLY,
    },
    "tb303":    {
        "default":  _tb303.PATTERNS,
        "acid8":    _tb303.PATTERNS_ACID8,
        "squelch":  _tb303.PATTERNS_SQUELCH,
    },
    "octatrack": {
        "default":  _octatrack.PATTERNS,
        "live":     _octatrack.PATTERNS_LIVE,
        "scene_b":  _octatrack.PATTERNS_SCENE_B,
    },
}


def list_designs() -> None:
    """Affiche les designs et patterns disponibles."""
    print("\n╔══════════════════════════════════════════════╗")
    print("║        Synthiker — Designs disponibles       ║")
    print("╠══════════════════════════════════════════════╣")
    for key, info in DESIGNS.items():
        patterns = list(_EXTRA_PATTERNS[key].keys())
        print(f"║  {key:<10}  {info['label']:<28}  ║")
        print(f"║             Patterns : {', '.join(patterns):<22} ║")
        print(f"║             Patch    : {info['patch']:<22} ║")
        print("╠══════════════════════════════════════════════╣")
    print("╚══════════════════════════════════════════════╝\n")


def send_encoder_defaults(pd_client, oled_client, defaults: list[int]) -> None:
    """Envoie les valeurs d'encodeurs par défaut du design via OSC."""
    for idx, val in enumerate(defaults):
        pd_client.send_message(ADDR_ENC.format(idx), val)
        oled_client.send_message(ADDR_ENC.format(idx), val)
    print(f"[DESIGN] Encodeurs initialisés ({len(defaults)} valeurs envoyées)")


def run_sequencer(patterns: dict[str, list[int]], bpm: int, track_names: list[str]) -> None:
    """Boucle séquenceur 16 pas avec les patterns du design sélectionné."""
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
        description="Sélecteur de design Synthiker → lance le séquenceur avec le design choisi"
    )
    parser.add_argument(
        "--design", choices=list(DESIGNS.keys()),
        default="tr808",
        help="Design à charger (défaut : tr808)",
    )
    parser.add_argument(
        "--pattern", default="default",
        help="Nom du pattern alternatif (défaut : default)",
    )
    parser.add_argument(
        "--bpm", type=int, default=None,
        help="Tempo en BPM (défaut : valeur recommandée du design)",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Liste les designs et patterns disponibles, puis quitte",
    )
    parser.add_argument(
        "--no-seq", action="store_true",
        help="N'initialise que les encodeurs sans démarrer le séquenceur",
    )
    args = parser.parse_args()

    if args.list:
        list_designs()
        return

    design_key = args.design
    design_info = DESIGNS[design_key]
    available_patterns = _EXTRA_PATTERNS[design_key]

    if args.pattern not in available_patterns:
        print(f"[ERREUR] Pattern inconnu '{args.pattern}' pour le design '{design_key}'.")
        print(f"         Patterns disponibles : {', '.join(available_patterns)}")
        sys.exit(1)

    patterns = available_patterns[args.pattern]
    bpm_map = {"tr808": _tr808.DEFAULT_BPM, "elektron": _elektron.DEFAULT_BPM,
               "tb303": _tb303.DEFAULT_BPM, "octatrack": _octatrack.DEFAULT_BPM}
    bpm = args.bpm or bpm_map[design_key]

    print(f"\n╔══════════════════════════════════════════════╗")
    print(f"║  Design  : {design_info['label']:<33}║")
    print(f"║  Pattern : {args.pattern:<33}║")
    print(f"║  BPM     : {bpm:<33}║")
    print(f"║  Patch Pd: {design_info['patch']:<33}║")
    print(f"╚══════════════════════════════════════════════╝")
    print(f"\n  → Ouvre le patch dans Pure Data :")
    print(f"    pd {design_info['patch']}\n")

    if design_key == "octatrack":
        print("  ── Mode Octatrack ──────────────────────────────")
        print("  Scènes A/B : utilise fake_panel.py --octatrack")
        print("    P1 → Scène A   P2 → Scène B   P3 → Morph A↔B")
        print("    ENC 11 (M3)   → crossfader /oct/scene")
        print("    1-8 + molette → P-lock sur le step courant")
        print("  ────────────────────────────────────────────────\n")

    pd_client = make_pd_client()
    oled_client = make_oled_client()
    send_encoder_defaults(pd_client, oled_client, design_info["encoder_defaults"])

    if args.no_seq:
        print("[DESIGN] Mode --no-seq : encodeurs initialisés, séquenceur non démarré.")
        return

    run_sequencer(patterns, bpm, design_info["tracks"])


if __name__ == "__main__":
    main()
