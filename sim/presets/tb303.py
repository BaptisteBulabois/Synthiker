"""sim/presets/tb303.py — Patterns et réglages pour le design Roland TB-303 Acid Bass.

La TB-303 est un synthétiseur basse monophonique. Ici la piste 0 ("bass") est active,
les pistes 1-3 restent silencieuses. Le patch synth_tb303.pd est un drone basse
contrôlé par encodeurs, pas un séquenceur de drums.

Encodeurs dans synth_tb303.pd :
  ENC 0  → pitch  (50–500 Hz)
  ENC 1  → résonnance Q  (0–30)
  ENC 3  → coupure filtre  (100–4000 Hz)
  ENC 4  → volume  (0–1)
"""

# ---------------------------------------------------------------------------
# Patterns 16 pas — la piste "bass" déclenche des notes à chaque step actif.
# Les autres pistes sont inutilisées (synth_tb303.pd ne les écoute pas).
# ---------------------------------------------------------------------------

#: Ligne acid classique — doubles croches rebondissantes
PATTERNS: dict[str, list[int]] = {
    "bass":  [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
    "pad2":  [0] * 16,
    "pad3":  [0] * 16,
    "pad4":  [0] * 16,
}

#: Ligne acid "boucle de 8"
PATTERNS_ACID8: dict[str, list[int]] = {
    "bass":  [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0],
    "pad2":  [0] * 16,
    "pad3":  [0] * 16,
    "pad4":  [0] * 16,
}

#: Ligne acid "squelch" (très rapide, typique 303)
PATTERNS_SQUELCH: dict[str, list[int]] = {
    "bass":  [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1],
    "pad2":  [0] * 16,
    "pad3":  [0] * 16,
    "pad4":  [0] * 16,
}

# ---------------------------------------------------------------------------
# Valeurs initiales des encodeurs (0..127)
# Mappées sur synth_tb303.pd :
#   ENC 0 → pitch (expr: val/127*450+50)
#   ENC 1 → résonnance (expr: val/127*30)
#   ENC 3 → coupure filtre (expr: val/127*3900+100)
#   ENC 4 → volume (expr: val/127)
# ---------------------------------------------------------------------------

ENCODER_DEFAULTS: list[int] = [
    57,   # 0  PITCH → ~252 Hz (environ B3/C4)
    30,   # 1  RES   → Q ≈ 7 (légèrement résonant)
    0,    # 2  —     (non utilisé)
    35,   # 3  CUT   → ≈1175 Hz (filtre mi-fermé, son "acid")
    90,   # 4  AMP   → volume élevé
    64,   # 5–11 : non utilisés dans TB-303
    64,
    64,
    64,
    64,
    64,
    64,
]

# ---------------------------------------------------------------------------
# BPM recommandé (acid house / techno)
# ---------------------------------------------------------------------------
DEFAULT_BPM: int = 138
