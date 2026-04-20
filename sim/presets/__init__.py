"""sim/presets — Patterns et valeurs d'encodeurs Synthiker (design Octatrack)."""

from sim.presets.octatrack import PATTERNS as OCT_PATTERNS, ENCODER_DEFAULTS as OCT_DEFAULTS

DESIGNS: dict[str, dict] = {
    "octatrack": {
        "label": "Elektron Octatrack",
        "patch": "pd_patches/synth_octatrack.pd",
        "patterns": OCT_PATTERNS,
        "encoder_defaults": OCT_DEFAULTS,
        "tracks": ["bd", "sd", "hat", "clap", "bass", "lead", "chord", "fx"],
    },
}
