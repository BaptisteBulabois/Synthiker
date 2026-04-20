# 🎛️ Synthiker — Octatrack DIY (PC Simulator)

Synthiker est une **groovebox DIY type Elektron Octatrack** entièrement open-source, combinant :
- **Pure Data** (moteur audio temps-réel, vanilla pur)
- **8 pistes** : percussions (BD/SD/HH/CL) + mélodie (BASS/LEAD/CHORD/FX)
- **Scènes A/B** avec crossfader et morphing progressif
- **P-locks** (parameter locks par step)
- **IA Markov** (génération de patterns, Magenta GrooVAE en PR #3)
- **Mode Tracker** (séquenceur pas-à-pas façon Polyend Tracker)
- Cible finale : **Raspberry Pi 5** + HAT audio I²S (HiFiBerry DAC2 Pro)

Cette PR = **couche de simulation PC** : teste tout le pipeline logiciel **avant d'acheter le hardware**.  
L'architecture OSC sera identique sur le Pi — **aucun code ne sera jeté**.

---

## 🏗️ Architecture

```
[fake_panel.py --octatrack] --OSC 5005--> [Pure Data synth_octatrack.pd]
[Pure Data synth_octatrack.pd] --> [audio 8 pistes]
                                        ^
[sequencer.py] / [tracker_mode.py] -----|
                                        |
[ai_gen.py (Markov/Magenta GrooVAE)] --|

[oled_emu.py] <--OSC 5006-- (tous les modules)
```

Tous les modules communiquent via **OSC (Open Sound Control)** sur localhost — même protocole que sur le Raspberry Pi 5.

---

## 📁 Arborescence

```
Synthiker/
├── README.md
├── LICENSE
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── sim/
│   ├── __init__.py
│   ├── osc_bridge.py           # Helpers OSC partagés (lit PD_HOST)
│   ├── fake_panel.py           # UI mock PyGame (12 encodeurs + 8 boutons + mode Octatrack)
│   ├── sequencer.py            # Séquenceur 16 pas 8 pistes → OSC (BPM 128)
│   ├── design_selector.py      # CLI lanceur Octatrack (--pattern, --bpm)
│   ├── tracker_mode.py         # Mode tracker JSON → OSC
│   ├── ai_gen.py               # IA fallback Markov → OSC
│   ├── oled_emu.py             # Émulateur OLED (luma.emulator)
│   ├── backend_supervisor.py   # Superviseur Docker (seq + IA + tracker)
│   └── presets/
│       ├── __init__.py         # Registre DESIGNS (octatrack)
│       └── octatrack.py        # Patterns + scènes A/B + BPM
├── pd_patches/
│   ├── synth_main.pd           # Patch Pd vanilla générique (PR #1)
│   ├── synth_octatrack.pd      # Patch Pd 8 pistes Octatrack
│   └── modules/
│       └── README.md           # Placeholder modules avancés (PR #3)
├── docs/
│   ├── osc_protocol.md
│   ├── simulation_guide.md
│   ├── synth_designs.md        # Documentation design Octatrack
│   ├── docker_guide.md         # Guide Docker hybride Windows
│   └── roadmap.md
└── scripts/
    ├── run_sim.sh              # Lance tout d'un coup (local, mode Octatrack)
    ├── docker_run.ps1          # Lanceur Docker (Windows PowerShell)
    └── docker_run.sh           # Lanceur Docker (bash)
```

---

## 🚀 Installation

### Prérequis

- **Python 3.11+**
- **Pure Data vanilla** ≥ 0.54
  - macOS : `brew install --cask pd`
  - Linux : `sudo apt install puredata`
  - Windows / autre : [puredata.info](https://puredata.info/downloads)

### Setup Python

```bash
git clone https://github.com/BaptisteBulabois/Synthiker.git
cd Synthiker

# Créer et activer le venv
python3.11 -m venv venv
source venv/bin/activate        # Linux/macOS
# .\venv\Scripts\activate       # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---

## ▶️ Lancer la simulation

### Option 1 — Script automatique (recommandé)

```bash
chmod +x scripts/run_sim.sh

# Terminal 1 : ouvre Pure Data et active le DSP (ctrl+/ ou cocher "DSP")
pd pd_patches/synth_octatrack.pd

# Terminal 2 : lance toute la stack Python
bash scripts/run_sim.sh
```

### Option 2 — Composants à la main

```bash
# Terminal 1
pd pd_patches/synth_octatrack.pd

# Terminal 2 : émulateur OLED
python sim/oled_emu.py

# Terminal 3 : interface graphique (mode Octatrack)
python sim/fake_panel.py --octatrack

# Terminal 4 : séquenceur 8 pistes
python sim/sequencer.py

# Terminal 5 (optionnel) : sélecteur avec pattern alternatif
python sim/design_selector.py --pattern live

# Terminal 6 (optionnel) : génération IA
python sim/ai_gen.py

# Terminal 7 (optionnel) : mode tracker
python sim/tracker_mode.py
```

> ⚠️ **Active le DSP dans Pure Data** (Ctrl+/ ou menu Media → DSP) sinon tu n'entendras rien.

---

## 🎮 Contrôles `fake_panel.py --octatrack`

| Action | Effet |
|---|---|
| **Molette souris** | Incrémenter / décrémenter la valeur de l'encodeur sélectionné (0..127) |
| **Q** | Encodeur précédent |
| **W** | Encodeur suivant |
| **1..8** | Boutons PAD (REC, PLAY, STOP, P1, P2, P3, P4, MODE) |
| **P1 (4)** | Scène A (encodeurs → ENCODER_DEFAULTS_A) |
| **P2 (5)** | Scène B (encodeurs → ENCODER_DEFAULTS_B) |
| **P3 (6)** | Morph progressif A↔B |
| **ENC 11 (M3)** | Crossfader `/oct/scene` 0.0–1.0 |
| **Tenir 1-8 + molette** | P-lock sur le step correspondant |
| **Échap** | Quitter |

---

## 🐳 Docker (Windows, approche hybride)

Vous pouvez faire tourner les composants **backend** (sequencer, IA Markov, tracker) dans un container Docker sur Windows, tout en gardant **Pure Data** (audio) et **fake_panel** (UI) sur l'hôte.

### Démarrage rapide

```powershell
# Prérequis : Docker Desktop installé et Pure Data lancé avec DSP activé
docker compose up --build
```

Ou avec le script PowerShell inclus :

```powershell
.\scripts\docker_run.ps1
```

### Documentation complète

👉 [docs/docker_guide.md](docs/docker_guide.md)

Le guide couvre les prérequis, la configuration du pare-feu, le dépannage du port 5005 et la vérification des paquets OSC.

---

## 🗺️ Roadmap

| Phase | Status | Contenu |
|---|---|---|
| **PR #1** | ✅ | Simu PC Octatrack (fake_panel --octatrack, sequencer 8 pistes, tracker, IA Markov, patch octatrack.pd) |
| **PR #2** | ⏳ | Firmware RPi 5 : `gpio_control.py` + crossfader physique + OLED scènes, même code grâce à `GPIOZERO_PIN_FACTORY=mock` |
| **PR #3** | ⏳ | 12 modules Pd Octatrack (FM, granular, scene morpher, p-lock interpolation) + Magenta GrooVAE (8 pistes) |
| **PR #4** | ⏳ | Hardware : KiCAD PCB + crossfader linéaire + ADS1115, STL boîtier façon Octatrack, BOM ~328-400€ |

> Ne rien acheter avant d'avoir validé la simu PC ! 💡

---

## 📜 Licence

MIT © 2026 Baptiste Bulabois — voir [LICENSE](LICENSE)
