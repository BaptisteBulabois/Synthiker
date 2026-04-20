"""sim/presets/tr808.py — Patterns et réglages pour le design Roland TR-808.

Quatre voix : BD (Bass Drum), SD (Snare Drum), CH (Closed Hi-Hat), CB (Cowbell).
Les patterns suivent la numérotation des pistes du séquenceur (piste 0..3).
"""

# ---------------------------------------------------------------------------
# Patterns 16 pas — indexés par nom de piste
# ---------------------------------------------------------------------------

#: Rythme "quatre-au-sol" classique (four-on-the-floor)
PATTERNS: dict[str, list[int]] = {
    "bd": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    "sd": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "ch": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    "cb": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
}

#: Rythme "boom bap" (hip-hop / breakbeat)
PATTERNS_BOOMBAP: dict[str, list[int]] = {
    "bd": [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],
    "sd": [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "ch": [1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
    "cb": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
}

#: Rythme "shuffle" (R&B / funk)
PATTERNS_SHUFFLE: dict[str, list[int]] = {
    "bd": [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    "sd": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    "ch": [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    "cb": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
}

# ---------------------------------------------------------------------------
# Valeurs initiales des encodeurs (0..127)
# Ordre : OSC, PITCH, WAVE, CUT, AMP, ENV-A, ENV-D, ENV-S, ENV-R, M1, M2, M3
# ---------------------------------------------------------------------------

ENCODER_DEFAULTS: list[int] = [
    64,   # 0  PITCH — contrôle la fréquence (routing: enc 0 → pitch_ctrl 100-500Hz)
    64,   # 1  PITCH — milieu de gamme
    0,    # 2  WAVE — non utilisé
    80,   # 3  CUT — filtre ouvert (≈3800Hz)
    100,  # 4  AMP — volume élevé
    64,   # 5  ENV-A
    64,   # 6  ENV-D
    64,   # 7  ENV-S
    64,   # 8  ENV-R
    64,   # 9  M1
    64,   # 10 M2
    64,   # 11 M3
]

# ---------------------------------------------------------------------------
# BPM recommandé
# ---------------------------------------------------------------------------
DEFAULT_BPM: int = 120
