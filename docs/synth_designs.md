# Design Octatrack — Synthiker

Synthiker est construit autour d'un seul design : l'**Elektron Octatrack**.
Ce document décrit le patch Pure Data, les patterns et tous les contrôles disponibles.

---

## Vue d'ensemble

| Paramètre | Valeur |
|---|---|
| **Fichier Pd** | `pd_patches/synth_octatrack.pd` |
| **Style** | Groovebox 8 pistes + scènes A/B |
| **BPM suggéré** | 128 |
| **Pistes** | BD / SD / HH / CL + BASS / LEAD / CHORD / FX |

---

## Voix (8 pistes)

### Groupe percussions (pistes 0–3)

| Piste | Voix | Synthèse |
|---|---|---|
| 0 | **BD** — Bass Drum FM | Sinus 1 kHz → 80 Hz en 15 ms (transiente FM-like) + env. 350 ms |
| 1 | **SD** — Snare Snap | Bruit court BP 300 Hz (15 ms) + bruit aigu HP 2 kHz (80 ms) |
| 2 | **HH** — Hi-Hat Métallique | Bruit filtré (BP 10 kHz), decay 250 ms |
| 3 | **CL** — Clap Triple | Triple rafale de bruit (0→3→6 ms) + queue 80 ms |

### Groupe mélodie (pistes 4–7)

| Piste | Voix | Synthèse |
|---|---|---|
| 4 | **BASS** | Onde en dents-de-scie (phasor~ 110 Hz) + env. amplitude 300 ms |
| 5 | **LEAD** | Sinusoïde (osc~ 440 Hz) + env. courte 80 ms |
| 6 | **CHORD** | Trois oscillateurs (220 / 277 / 330 Hz) + env. 400 ms |
| 7 | **FX** | Bruit filtré (BP 800 Hz, Q=2) + env. 150 ms |

---

## Patterns

| Nom | Description |
|---|---|
| `default` | Pattern 4/4 standard — grosse caisse sur les temps, basse pulsée |
| `live` | Pattern syncopé, style performance Octatrack |
| `scene_b` | Variante dense Scène B — tous les éléments actifs |

---

## Scènes A et B

Chaque scène définit un jeu complet de 12 valeurs d'encodeurs :

| Scène | Ambiance | CUT | RES | ENV-D | M2 (Movement) |
|---|---|---|---|---|---|
| **A** | Chaud, groove | 90 (ouvert) | 5 (doux) | 70 (medium) | 40 (bas) |
| **B** | Froid, agressif | 50 (fermé) | 20 (rapide) | 100 (long) | 100 (élevé) |

Le **crossfader** (encodeur M3, index 11) envoie `/oct/scene <0.0–1.0>` vers Pure Data :
- `0.0` → 100 % Scène A
- `1.0` → 100 % Scène B
- Valeurs intermédiaires → morphing progressif

---

## P-locks (Parameter Locks)

Les p-locks permettent de fixer la valeur d'un encodeur pour un step spécifique :

```
Maintenir la touche 1-8 (= step 0-7) + molette → enregistre le p-lock
```

Les p-locks stockés sont affichés dans la console. Le compteur de p-locks actifs
est visible dans la barre d'info en bas du fake_panel.

---

## Lancement

```bash
# Patch Pure Data
pd pd_patches/synth_octatrack.pd

# Séquenceur 8 pistes (BPM 128 par défaut)
python sim/design_selector.py

# Avec un pattern alternatif
python sim/design_selector.py --pattern live

# Interface Octatrack complète (scènes A/B, crossfader, p-locks)
python sim/fake_panel.py --octatrack

# Tout d'un coup
bash scripts/run_sim.sh
```

---

## Contrôles `fake_panel.py --octatrack`

| Contrôle | Action |
|---|---|
| **P1** (touche 4) | Applique immédiatement la Scène A |
| **P2** (touche 5) | Applique immédiatement la Scène B |
| **P3** (touche 6) | Lance le morphing progressif vers l'autre scène |
| **P4** (touche 7) | Cycle parmi les patterns (affichage console) |
| **MODE** (touche 8) | Bascule l'affichage OLED entre vue scène et vue info |
| **ENC 11 (M3)** + molette | Crossfader `/oct/scene` 0.0–1.0 |
| **Tenir 1-8** + molette | P-lock sur le step correspondant (step 1=touche 1, etc.) |

> **Astuce** : lance le séquenceur (`design_selector.py`) dans un terminal
> et le fake_panel (`--octatrack`) dans un autre. Utilise P3 en live pour des
> transitions fluides entre les deux scènes, ou M3 pour des crossfades manuels.

---

## Architecture des fichiers

```
Synthiker/
├── pd_patches/
│   ├── synth_main.pd          # Patch générique (PR #1)
│   └── synth_octatrack.pd     # ← Elektron Octatrack (8 pistes + scènes A/B)
└── sim/
    ├── design_selector.py     # ← CLI lanceur Octatrack (--pattern, --bpm)
    ├── fake_panel.py          # ← Interface graphique (--octatrack obligatoire)
    └── presets/
        ├── __init__.py        # ← Registre DESIGNS (octatrack uniquement)
        └── octatrack.py       # ← Patterns + scènes A/B + BPM
```
