# Designs de synthétiseurs — TR-808, Elektron, TB-303, Octatrack

Ce document décrit les quatre designs de synthétiseurs disponibles dans la branche
`feature/synth-designs`, chacun avec son patch Pure Data et ses presets Python.

---

## Vue d'ensemble

| Design | Fichier Pd | Style | BPM suggéré |
|---|---|---|---|
| **TR-808** | `pd_patches/synth_tr808.pd` | Drum machine analogique classique | 120 |
| **Elektron** | `pd_patches/synth_elektron.pd` | Drum machine numérique moderne | 133 |
| **TB-303** | `pd_patches/synth_tb303.pd` | Basse acid monophonique | 138 |
| **Octatrack** | `pd_patches/synth_octatrack.pd` | Groovebox 8 pistes + scènes A/B | 128 |

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

## 4. Elektron Octatrack (`synth_octatrack.pd`)

### Caractéristiques

Inspiré de l'Elektron Octatrack MkII (2015) : groovebox 8 pistes, scènes A/B avec
crossfader, et p-locks (parameter locks) permettant de varier les paramètres par step.
Ce design est adapté au moteur de synthèse de Synthiker (sans sampler).

#### Voix (8 pistes)

**Groupe percussions (pistes 0–3)**

| Piste | Voix | Synthèse |
|---|---|---|
| 0 | **BD** — Bass Drum FM | Sinus 1 kHz → 80 Hz en 15 ms (transiente FM-like) + env. 350 ms |
| 1 | **SD** — Snare Snap | Bruit court BP 300 Hz (15 ms) + bruit aigu HP 2 kHz (80 ms) |
| 2 | **HH** — Hi-Hat Métallique | Bruit filtré (BP 10 kHz), decay 250 ms |
| 3 | **CL** — Clap Triple | Triple rafale de bruit (0→3→6 ms) + queue 80 ms |

**Groupe mélodie (pistes 4–7)**

| Piste | Voix | Synthèse |
|---|---|---|
| 4 | **BASS** | Onde en dents-de-scie (phasor~ 110 Hz) + env. amplitude 300 ms |
| 5 | **LEAD** | Sinusoïde (osc~ 440 Hz) + env. courte 80 ms |
| 6 | **CHORD** | Trois oscillateurs (220 / 277 / 330 Hz) + env. 400 ms |
| 7 | **FX** | Bruit filtré (BP 800 Hz, Q=2) + env. 150 ms |

#### Patterns disponibles

| Nom | Description |
|---|---|
| `default` | Pattern 4/4 standard — grosse caisse sur les temps, basse pulsée |
| `live` | Pattern syncopé, style performance Octatrack |
| `scene_b` | Variante dense Scène B — tous les éléments actifs |

#### Scènes A et B

Chaque scène définit un jeu complet de 12 valeurs d'encodeurs :

| Scène | Ambiance | CUT | RES | ENV-D | M2 (Movement) |
|---|---|---|---|---|---|
| **A** | Chaud, groove | 90 (ouvert) | 5 (doux) | 70 (medium) | 40 (bas) |
| **B** | Froid, agressif | 50 (fermé) | 20 (rapide) | 100 (long) | 100 (élevé) |

Le **crossfader** (encodeur M3, index 11) envoie `/oct/scene <0.0–1.0>` vers Pure Data :
- `0.0` → 100 % Scène A
- `1.0` → 100 % Scène B
- Valeurs intermédiaires → morphing progressif

#### P-locks (Parameter Locks)

Les p-locks permettent de fixer la valeur d'un encodeur pour un step spécifique :

```
Maintenir la touche 1-8 (= step 0-7) + molette → enregistre le p-lock
```

Les p-locks stockés sont affichés dans la console. Le compteur de p-locks actifs
est visible dans la barre d'info en bas du fake_panel.

#### Commande

```bash
# Patch Pure Data
pd pd_patches/synth_octatrack.pd

# Séquenceur 8 pistes
python sim/design_selector.py --design octatrack --bpm 128

# Avec un pattern alternatif
python sim/design_selector.py --design octatrack --pattern live

# Interface Octatrack complète (scènes A/B, crossfader, p-locks)
python sim/fake_panel.py --octatrack
```

#### Contrôles en mode Octatrack (`--octatrack`)

| Contrôle | Action |
|---|---|
| **P1** (touche 4) | Applique immédiatement la Scène A |
| **P2** (touche 5) | Applique immédiatement la Scène B |
| **P3** (touche 6) | Lance le morphing progressif vers l'autre scène |
| **P4** (touche 7) | Cycle parmi les patterns (affichage console) |
| **MODE** (touche 8) | Bascule l'affichage OLED entre vue scène et vue info |
| **ENC 11 (M3)** + molette | Crossfader `/oct/scene` 0.0–1.0 |
| **Tenir 1-8** + molette | P-lock sur le step correspondant (step 1=touche 1, etc.) |

> **Astuce Octatrack** : lance le séquenceur (`design_selector.py`) dans un terminal
> et le fake_panel (`--octatrack`) dans un autre. Utilise P3 en live pour des
> transitions fluides entre les deux scènes, ou M3 pour des crossfades manuels.

---

## Sélecteur de design (`sim/design_selector.py`)

```
usage: python sim/design_selector.py [--design {tr808,elektron,tb303,octatrack}]
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
│   ├── synth_tb303.pd         # ← Roland TB-303 Acid Bass
│   └── synth_octatrack.pd     # ← Elektron Octatrack (8 pistes + scènes A/B)
└── sim/
    ├── design_selector.py     # ← CLI sélecteur de design
    ├── fake_panel.py          # ← Interface graphique (--octatrack pour mode Octatrack)
    └── presets/
        ├── __init__.py        # ← Registre DESIGNS
        ├── tr808.py           # ← Patterns + encodeurs TR-808
        ├── elektron.py        # ← Patterns + encodeurs Elektron
        ├── tb303.py           # ← Patterns + encodeurs TB-303
        └── octatrack.py       # ← Patterns + scènes A/B Octatrack
```
