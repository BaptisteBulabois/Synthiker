"""sim/presets — Patterns et valeurs d'encodeurs par design Synthiker."""

from sim.presets.tr808 import PATTERNS as TR808_PATTERNS, ENCODER_DEFAULTS as TR808_DEFAULTS
from sim.presets.elektron import PATTERNS as ELEKTRON_PATTERNS, ENCODER_DEFAULTS as ELEKTRON_DEFAULTS
from sim.presets.tb303 import PATTERNS as TB303_PATTERNS, ENCODER_DEFAULTS as TB303_DEFAULTS
from sim.presets.octatrack import PATTERNS as OCT_PATTERNS, ENCODER_DEFAULTS as OCT_DEFAULTS

DESIGNS: dict[str, dict] = {
    "tr808": {
        "label": "Roland TR-808",
        "patch": "pd_patches/synth_tr808.pd",
        "patterns": TR808_PATTERNS,
        "encoder_defaults": TR808_DEFAULTS,
        "tracks": ["bd", "sd", "ch", "cb"],
    },
    "elektron": {
        "label": "Elektron / Digitakt",
        "patch": "pd_patches/synth_elektron.pd",
        "patterns": ELEKTRON_PATTERNS,
        "encoder_defaults": ELEKTRON_DEFAULTS,
        "tracks": ["kick", "snare", "hat", "clap"],
    },
    "tb303": {
        "label": "Roland TB-303 Acid Bass",
        "patch": "pd_patches/synth_tb303.pd",
        "patterns": TB303_PATTERNS,
        "encoder_defaults": TB303_DEFAULTS,
        "tracks": ["bass", "bass", "bass", "bass"],
    },
    "octatrack": {
        "label": "Elektron Octatrack",
        "patch": "pd_patches/synth_octatrack.pd",
        "patterns": OCT_PATTERNS,
        "encoder_defaults": OCT_DEFAULTS,
        "tracks": ["bd", "sd", "hat", "clap", "bass", "lead", "chord", "fx"],
    },
}
