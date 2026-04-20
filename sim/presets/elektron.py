"""sim/presets/elektron.py — Patterns et réglages pour le design Elektron/Digitakt.

Quatre voix : Kick (FM), Snare (snap), Hi-Hat (métallique), Clap (triple burst).
Inspiré du style Elektron Digitakt : rythmes syncopés, vélocités variées, temps fort décalé.
"""

# ---------------------------------------------------------------------------
# Patterns 16 pas — indexés par nom de piste
# ---------------------------------------------------------------------------

#: Pattern principal : kick syncopé, snare off-beat, hat dense, clap sur 2 et 4
PATTERNS: dict[str, list[int]] = {
    "kick":  [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    "snare": [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
    "hat":   [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1],
    "clap":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
}

#: Pattern "minimal techno" (Elektron Digitakt typique)
PATTERNS_MINIMAL: dict[str, list[int]] = {
    "kick":  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "hat":   [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0],
    "clap":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
}

#: Pattern "polyrhythmique" (inspiré du style Octatrack)
PATTERNS_POLY: dict[str, list[int]] = {
    "kick":  [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0],  # intervalle de 3 (5 accents/16 pas)
    "snare": [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],  # intervalle de 3 décalé
    "hat":   [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # quarters (4/4)
    "clap":  [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
}

# ---------------------------------------------------------------------------
# Valeurs initiales des encodeurs (0..127)
# ---------------------------------------------------------------------------

ENCODER_DEFAULTS: list[int] = [
    64,   # 0  OSC
    64,   # 1  PITCH
    0,    # 2  WAVE
    100,  # 3  CUT — filtre très ouvert (sons modernes, pas filtré)
    100,  # 4  AMP
    40,   # 5  ENV-A — attaque rapide
    80,   # 6  ENV-D — decay medium
    50,   # 7  ENV-S
    64,   # 8  ENV-R
    80,   # 9  M1 — Brightness
    50,   # 10 M2 — Movement
    30,   # 11 M3 — Density
]

# ---------------------------------------------------------------------------
# BPM recommandé (techno / house)
# ---------------------------------------------------------------------------
DEFAULT_BPM: int = 133
