"""
tracker_mode.py — Mode tracker JSON → OSC pour Synthiker.

Format du fichier JSON :
    {
        "bpm": 120,
        "rows": [
            [{"note": "C-3", "vel": 100, "fx": "--"}, ...],  // 4 channels
            ...                                               // 16 rows
        ]
    }

Notes spéciales :
    "---" → silence (pas de trigger)
    "C-3" → MIDI 48, "C#3" → 49, etc.

Usage :
    python sim/tracker_mode.py --bpm 130 --pattern tracker_pattern.json
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, __file__.replace("/sim/tracker_mode.py", ""))

from sim.osc_bridge import make_pd_client, ADDR_NOTE, ADDR_MODE

# ---------------------------------------------------------------------------
# Pattern par défaut (16 lignes × 4 canaux)
# ---------------------------------------------------------------------------
DEFAULT_PATTERN = {
    "bpm": 120,
    "rows": [
        [{"note": "C-3", "vel": 100, "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "G-3", "vel": 80,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "E-3", "vel": 90,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "F-3", "vel": 95,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "C-4", "vel": 85,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "G-3", "vel": 100, "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "B-2", "vel": 70,  "fx": "--"}],

        [{"note": "A-3", "vel": 90,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "E-3", "vel": 80,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "C-4", "vel": 95,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "G-3", "vel": 100, "fx": "--"}],

        [{"note": "D-3", "vel": 85,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "A-3", "vel": 90,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "F-3", "vel": 80,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "D-4", "vel": 75,  "fx": "--"}],

        [{"note": "G-3", "vel": 100, "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "C-3", "vel": 95,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "A-3", "vel": 85,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "E-3", "vel": 80,  "fx": "--"}],

        [{"note": "E-3", "vel": 90,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "B-2", "vel": 70,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "D-3", "vel": 100, "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "F-3", "vel": 85,  "fx": "--"}],

        [{"note": "C-4", "vel": 95,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "G-3", "vel": 80,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "B-3", "vel": 90,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "C-3", "vel": 100, "fx": "--"}],

        [{"note": "A-2", "vel": 75,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "E-4", "vel": 85,  "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"}],

        [{"note": "---", "vel": 0,   "fx": "--"},
         {"note": "C-3", "vel": 100, "fx": "--"},
         {"note": "---", "vel": 0,   "fx": "--"},
         {"note": "G-3", "vel": 90,  "fx": "--"}],
    ]
}

# ---------------------------------------------------------------------------
# Conversion note → MIDI
# ---------------------------------------------------------------------------
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_midi(note_str: str) -> int | None:
    """Convertit une chaîne de note en numéro MIDI.

    Exemples :
        "C-3"  → 48
        "C#3"  → 49
        "G-4"  → 67
        "---"  → None (silence)
    """
    if not note_str or note_str.startswith("---"):
        return None

    # Enlever le séparateur '-' entre le nom de note et l'octave
    s = note_str.replace("-", "").strip()
    if not s:
        return None

    # Extraire le nom de note (1 ou 2 caractères) et l'octave
    if len(s) >= 2 and s[1] == "#":
        name = s[:2]
        octave_str = s[2:]
    else:
        name = s[0]
        octave_str = s[1:]

    name = name.upper()
    if name not in NOTE_NAMES:
        return None

    try:
        octave = int(octave_str)
    except ValueError:
        return None

    semitone = NOTE_NAMES.index(name)
    # Convention tracker : "C-3" signifie C à l'octave 3.
    # Le '-' est un séparateur visuel (format Polyend/OpenMPT), pas un signe moins.
    # Formule MIDI standard : C-1=0, C0=12, C1=24, C3=48, C4=60 (Do central).
    # 12 * (octave + 1) car MIDI débute à C-1 = 0 (octave -1 dans la convention).
    return 12 * (octave + 1) + semitone


# ---------------------------------------------------------------------------
# Boucle tracker
# ---------------------------------------------------------------------------

def load_or_create_pattern(path: str) -> dict:
    """Charge le fichier JSON ou crée le pattern par défaut."""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            pattern = json.load(f)
        print(f"[TRACKER] Pattern chargé depuis '{path}'")
    else:
        pattern = DEFAULT_PATTERN
        with open(path, "w", encoding="utf-8") as f:
            json.dump(pattern, f, indent=2, ensure_ascii=False)
        print(f"[TRACKER] Pattern par défaut créé → '{path}'")
    return pattern


def run_tracker(bpm: int, pattern_path: str) -> None:
    """Boucle principale du mode tracker."""
    client = make_pd_client()
    pattern = load_or_create_pattern(pattern_path)

    bpm_effective = pattern.get("bpm", bpm)
    rows = pattern.get("rows", [])
    step_duration = 60.0 / (bpm_effective * 4)

    client.send_message(ADDR_MODE, "tracker")
    print(f"[TRACKER] Mode tracker — BPM={bpm_effective}, {len(rows)} lignes")
    print("[TRACKER] Ctrl+C pour arrêter\n")

    try:
        while True:
            for row_idx, row in enumerate(rows):
                print(f"[TRACKER] Row {row_idx:02d}: ", end="")
                for ch_idx, cell in enumerate(row):
                    note_str = cell.get("note", "---")
                    vel = cell.get("vel", 0)
                    midi = note_to_midi(note_str)
                    if midi is not None:
                        client.send_message(ADDR_NOTE, [midi, vel, ch_idx])
                        print(f"ch{ch_idx}:{note_str}({midi}) ", end="")
                    else:
                        print(f"ch{ch_idx}:---       ", end="")
                print(flush=True)
                time.sleep(step_duration)

    except KeyboardInterrupt:
        print("\n[TRACKER] Arrêt propre.")


def main() -> None:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(description="Mode tracker JSON → OSC Synthiker")
    parser.add_argument("--bpm", type=int, default=120,
                        help="Tempo BPM (écrasé par le champ bpm du JSON)")
    parser.add_argument("--pattern", type=str, default="tracker_pattern.json",
                        help="Chemin vers le fichier JSON de pattern")
    args = parser.parse_args()
    run_tracker(args.bpm, args.pattern)


if __name__ == "__main__":
    main()
