"""sim/presets/octatrack.py — Patterns et réglages pour le design Elektron Octatrack.

Huit pistes organisées en deux groupes :
  Percussions (0-3) : BD (kick FM), SD (snare snap), HH (hat métallique), CL (clap triple)
  Mélodie    (4-7) : BASS (dent-de-scie), LEAD (sinus), CHORD (3 oscillateurs), FX (bruit filtré)

Deux scènes (A et B) définissent chacune un jeu complet de 12 valeurs d'encodeurs.
L'encodeur M3 (index 11) sert de crossfader entre les deux scènes.
"""

# ---------------------------------------------------------------------------
# Patterns 16 pas — indexés par nom de piste
# ---------------------------------------------------------------------------

#: Pattern "4/4 standard" — grosse caisse sur les temps forts, basse pulsée
PATTERNS: dict[str, list[int]] = {
    "bd":    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    "sd":    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "hat":   [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    "clap":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "bass":  [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    "lead":  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    "chord": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "fx":    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
}

#: Pattern "live" — syncopé, style performance Octatrack
PATTERNS_LIVE: dict[str, list[int]] = {
    "bd":    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    "sd":    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    "hat":   [1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
    "clap":  [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
    "bass":  [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0],
    "lead":  [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    "chord": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "fx":    [0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
}

#: Pattern "scene_b" — dense, tous les éléments actifs (scène B typique Octatrack)
PATTERNS_SCENE_B: dict[str, list[int]] = {
    "bd":    [1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
    "sd":    [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    "hat":   [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
    "clap":  [0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    "bass":  [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    "lead":  [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
    "chord": [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1],
    "fx":    [1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0],
}

# ---------------------------------------------------------------------------
# Valeurs initiales des encodeurs — Scène A (groovy, son chaud)
# Ordre : OSC, PITCH, WAVE, CUT, AMP, ENV-A, ENV-D, ENV-S, ENV-R, M1, M2, M3
# ---------------------------------------------------------------------------

ENCODER_DEFAULTS_A: list[int] = [
    64,   # 0  OSC
    60,   # 1  PITCH — légèrement grave
    20,   # 2  WAVE — onde chaude
    90,   # 3  CUT  — filtre ouvert
    100,  # 4  AMP  — volume élevé
    5,    # 5  ENV-A — attaque quasi-instantanée
    70,   # 6  ENV-D — decay medium
    50,   # 7  ENV-S — sustain medium
    40,   # 8  ENV-R — release court
    80,   # 9  M1  — Brightness élevé
    40,   # 10 M2  — Movement bas
    0,    # 11 M3  — Crossfader à 0 = Scène A pure
]

#: Alias pour la compatibilité avec presets/__init__.py
ENCODER_DEFAULTS = ENCODER_DEFAULTS_A

# ---------------------------------------------------------------------------
# Valeurs initiales des encodeurs — Scène B (agressif, son froid et modulé)
# ---------------------------------------------------------------------------

ENCODER_DEFAULTS_B: list[int] = [
    80,   # 0  OSC
    75,   # 1  PITCH — plus aigu
    80,   # 2  WAVE — onde dure
    50,   # 3  CUT  — filtre plus fermé
    90,   # 4  AMP
    20,   # 5  ENV-A — attaque rapide
    100,  # 6  ENV-D — decay long
    30,   # 7  ENV-S — sustain bas
    80,   # 8  ENV-R — release plus long
    30,   # 9  M1  — Brightness bas
    100,  # 10 M2  — Movement élevé
    127,  # 11 M3  — Crossfader à 127 = Scène B pure
]

# ---------------------------------------------------------------------------
# BPM recommandé (techno / house électronique)
# ---------------------------------------------------------------------------
DEFAULT_BPM: int = 128
