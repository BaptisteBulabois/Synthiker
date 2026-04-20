# Designs de synthétiseurs — TR-808, Elektron, TB-303

Ce document décrit les trois designs de synthétiseurs disponibles dans la branche
`feature/synth-designs`, chacun avec son patch Pure Data et ses presets Python.

---

## Vue d'ensemble

| Design | Fichier Pd | Style | BPM suggéré |
|---|---|---|---|
| **TR-808** | `pd_patches/synth_tr808.pd` | Drum machine analogique classique | 120 |
| **Elektron** | `pd_patches/synth_elektron.pd` | Drum machine numérique moderne | 133 |
| **TB-303** | `pd_patches/synth_tb303.pd` | Basse acid monophonique | 138 |

---

## 1. Roland TR-808 (`synth_tr808.pd`)

### Caractéristiques

La TR-808 (1980) est une drum machine analogique devenue emblématique du hip-hop, de la house et du techno.

#### Voix

| Piste | Voix | Synthèse |
|---|---|---|
| 0 | **BD** — Bass Drum | Sinus 250 Hz → 50 Hz en 60 ms + env. ampli 500 ms |
| 1 | **SD** — Snare Drum | Sinus 200 Hz + bruit filtré (BP 1 kHz), mix 50/50 |
| 2 | **CH** — Closed Hi-Hat | Bruit filtré (HP 8 kHz), decay 50 ms |
| 3 | **CB** — Cowbell | Deux oscillateurs (540 Hz + 800 Hz), BP 800 Hz |

#### Patterns disponibles

| Nom | Description |
|---|---|
| `default` | Quatre-au-sol classique |
| `boombap` | Boom bap (hip-hop / breakbeat) |
| `shuffle` | Shuffle (R&B / funk) |

#### Commande

```bash
# Étape 1 — Ouvrir le patch Pure Data
pd pd_patches/synth_tr808.pd

# Étape 2 — Lancer le séquenceur avec le design TR-808
python sim/design_selector.py --design tr808 --bpm 120

# Avec un pattern alternatif
python sim/design_selector.py --design tr808 --pattern boombap
```

---

## 2. Elektron / Digitakt (`synth_elektron.pd`)

### Caractéristiques

Inspiré du Digitakt (2017) et des boîtes à rythmes Elektron : sons percussifs modernes,
transitoires précises, textures métalliques.

#### Voix

| Piste | Voix | Synthèse |
|---|---|---|
| 0 | **Kick FM** | Sinus 1 kHz → 80 Hz en 15 ms (transiente FM-like) + env. 350 ms |
| 1 | **Snare Snap** | Bruit court BP 300 Hz (15 ms) + bruit aigu HP 2 kHz (80 ms) |
| 2 | **Hi-Hat Métallique** | Bruit filtré (BP 10 kHz), decay 250 ms |
| 3 | **Clap Triple** | Triple rafale de bruit (0→3→6 ms) + queue 80 ms |

#### Patterns disponibles

| Nom | Description |
|---|---|
| `default` | Syncopé avec kick off-beat |
| `minimal` | Minimal techno (kick régulier) |
| `poly` | Polyrhythmique (inspiration Octatrack) |

#### Commande

```bash
pd pd_patches/synth_elektron.pd
python sim/design_selector.py --design elektron --bpm 133
python sim/design_selector.py --design elektron --pattern minimal
```

---

## 3. Roland TB-303 Acid Bass (`synth_tb303.pd`)

### Caractéristiques

La TB-303 (1981) est un synthétiseur basse monophonique célèbre pour le son "acid"
(squelch, resonance extrême). Contrairement aux deux autres designs, c'est une
**basse tonale continue** contrôlée par encodeurs, pas une machine à percussion.

#### Synthèse

```
[phasor~] → [×2] → [+~ -1]  (dent-de-scie −1..+1)
                         ↓
                      [vcf~]  filtre passe-bas résonant (Q 0–30)
                         ↓
                       [×~]   VCA (volume)
                         ↓
                      [dac~]
```

#### Mappages encodeurs

| Encodeur | Paramètre | Plage |
|---|---|---|
| ENC 0 | Pitch | 50–500 Hz |
| ENC 1 | Résonnance (Q) | 0–30 |
| ENC 3 | Coupure filtre | 100–4000 Hz |
| ENC 4 | Volume | 0–1 |

#### Patterns disponibles (triggers rythmiques)

| Nom | Description |
|---|---|
| `default` | Ligne acid rebondissante |
| `acid8` | Boucle acid de 8 |
| `squelch` | Squelch rapide (très typique 303) |

#### Commande

```bash
pd pd_patches/synth_tb303.pd
python sim/design_selector.py --design tb303 --bpm 138

# Avec fake_panel pour contrôler les encodeurs en temps réel
python sim/fake_panel.py
```

> **Astuce TB-303** : augmente le paramètre RES (ENC 1) progressivement
> et joue sur CUT (ENC 3) pour l'effet "acid". À Q > 20, le filtre peut auto-osciller.

---

## Sélecteur de design (`sim/design_selector.py`)

```
usage: python sim/design_selector.py [--design {tr808,elektron,tb303}]
                                     [--pattern NOM]
                                     [--bpm N]
                                     [--list]
                                     [--no-seq]
```

| Option | Description |
|---|---|
| `--design` | Design à charger (défaut : `tr808`) |
| `--pattern` | Nom du pattern alternatif (défaut : `default`) |
| `--bpm` | Tempo BPM (défaut : valeur recommandée du design) |
| `--list` | Liste tous les designs et patterns disponibles |
| `--no-seq` | Initialise uniquement les encodeurs sans démarrer le séquenceur |

---

## Architecture des fichiers

```
Synthiker/
├── pd_patches/
│   ├── synth_main.pd          # Design générique (PR #1)
│   ├── synth_tr808.pd         # ← Roland TR-808
│   ├── synth_elektron.pd      # ← Elektron / Digitakt
│   └── synth_tb303.pd         # ← Roland TB-303 Acid Bass
└── sim/
    ├── design_selector.py     # ← CLI sélecteur de design
    └── presets/
        ├── __init__.py        # ← Registre DESIGNS
        ├── tr808.py           # ← Patterns + encodeurs TR-808
        ├── elektron.py        # ← Patterns + encodeurs Elektron
        └── tb303.py           # ← Patterns + encodeurs TB-303
```
