# 🎛️ Synthiker — SynthModulAI Simulator (PC)

Synthiker est une **groovebox DIY type Digitakt** entièrement open-source, combinant :
- **Pure Data** (moteur audio temps-réel, vanilla pur)
- **IA Markov** (génération de patterns drums, Magenta en PR #3)
- **Mode Tracker** (séquenceur pas-à-pas façon Polyend Tracker)
- Cible finale : **Raspberry Pi 5** + HAT audio I²S (HiFiBerry DAC2 Pro)

Cette PR = **couche de simulation PC** : teste tout le pipeline logiciel **avant d'acheter le hardware**.  
L'architecture OSC sera identique sur le Pi — **aucun code ne sera jeté**.

---

## 🏗️ Architecture

```
[fake_panel.py] --OSC 5005--> [Pure Data synth_main.pd]
[Pure Data synth_main.pd] --> [audio]
                                       ^
[sequencer.py] / [tracker_mode.py] ----|
                                       |
[ai_gen.py (Markov/Magenta)] ----------|

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
├── requirements.txt
├── sim/
│   ├── __init__.py
│   ├── osc_bridge.py       # Helpers OSC partagés
│   ├── fake_panel.py       # UI mock PyGame (12 encodeurs + 8 boutons + OLED mock)
│   ├── sequencer.py        # Séquenceur 16 pas → OSC
│   ├── tracker_mode.py     # Mode tracker JSON → OSC
│   ├── ai_gen.py           # IA fallback Markov → OSC
│   └── oled_emu.py         # Émulateur OLED (luma.emulator)
├── pd_patches/
│   ├── synth_main.pd       # Patch Pd vanilla : netreceive OSC → osc~ + filtre
│   └── modules/
│       └── README.md       # Placeholder modules avancés (PR #3)
├── docs/
│   ├── osc_protocol.md
│   ├── simulation_guide.md
│   └── roadmap.md
└── scripts/
    └── run_sim.sh          # Lance tout d'un coup
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
pd pd_patches/synth_main.pd

# Terminal 2 : lance toute la stack Python
bash scripts/run_sim.sh
```

### Option 2 — Composants à la main

```bash
# Terminal 1
pd pd_patches/synth_main.pd

# Terminal 2 : émulateur OLED
python sim/oled_emu.py

# Terminal 3 : interface graphique
python sim/fake_panel.py

# Terminal 4 : séquenceur
python sim/sequencer.py --bpm 120

# Terminal 5 (optionnel) : génération IA
python sim/ai_gen.py

# Terminal 6 (optionnel) : mode tracker
python sim/tracker_mode.py
```

> ⚠️ **Active le DSP dans Pure Data** (Ctrl+/ ou menu Media → DSP) sinon tu n'entendras rien.

---

## 🎮 Contrôles `fake_panel.py`

| Action | Effet |
|---|---|
| **Molette souris** | Incrémenter / décrémenter la valeur de l'encodeur sélectionné (0..127) |
| **Q** | Encodeur précédent |
| **W** | Encodeur suivant |
| **1..8** | Boutons PAD (REC, PLAY, STOP, P1, P2, P3, P4, MODE) |
| **Échap** | Quitter |

---

## 🗺️ Roadmap

| Phase | Status | Contenu |
|---|---|---|
| **PR #1** | ✅ | Simu PC (fake_panel, sequencer, tracker, IA Markov, patch Pd vanilla) |
| **PR #2** | ⏳ | Firmware RPi 5 : `gpio_control.py` + systemd, même code grâce à `GPIOZERO_PIN_FACTORY=mock` |
| **PR #3** | ⏳ | 12 modules Pd avancés + Magenta IA (GPU / TPU) |
| **PR #4** | ⏳ | Hardware : KiCAD PCB, STL boîtier, BOM complet ~380-540€ |

> Ne rien acheter avant d'avoir validé la simu PC ! 💡

---

## 📜 Licence

MIT © 2026 Baptiste Bulabois — voir [LICENSE](LICENSE)
