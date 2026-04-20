# Guide de Simulation — Synthiker

Ce guide détaille comment lancer la simulation PC complète du pipeline Synthiker.

---

## 📋 Prérequis

| Outil | Version minimale | Installation |
|---|---|---|
| Python | 3.11 | [python.org](https://www.python.org/downloads/) |
| Pure Data | 0.54 (vanilla) | `brew install --cask pd` / `sudo apt install puredata` / [puredata.info](https://puredata.info) |
| SDL2 | (via pygame) | Inclus avec pygame sur la plupart des systèmes |

> ⚠️ **N'installez PAS** d'externals Pure Data (Cyclone, ELSE, etc.) — le patch `synth_main.pd` est Pd vanilla pur.

---

## 🔧 Installation

### 1. Cloner le repo

```bash
git clone https://github.com/BaptisteBulabois/Synthiker.git
cd Synthiker
```

### 2. Créer et activer le venv Python

```bash
# Créer le venv
python3.11 -m venv venv

# Activer (Linux / macOS)
source venv/bin/activate

# Activer (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

La commande installe :
- `python-osc` — envoi/réception OSC UDP
- `pygame` — interface graphique fake_panel
- `luma.emulator` + `luma.oled` — émulateur OLED
- `numpy` — calcul matriciel pour l'IA Markov
- `mido` + `python-rtmidi` — MIDI (utilisé en PR #2)

### 4. Rendre le script de lancement exécutable (Linux/macOS)

```bash
chmod +x scripts/run_sim.sh
```

---

## ▶️ Lancement étape par étape

### Étape 1 — Ouvrir Pure Data et activer le DSP

```bash
pd pd_patches/synth_octatrack.pd
```

Dans la fenêtre Pure Data :
- Allez dans **Media → Audio Settings** et vérifiez la carte son.
- Activez le DSP : **Media → DSP** (cocher) ou raccourci **Ctrl+/** (Linux/Windows) / **Cmd+/** (macOS).

> 🔊 Sans DSP activé, aucun son ne sortira même si les OSC arrivent.

### Étape 2 — Lancer l'émulateur OLED (optionnel)

```bash
python sim/oled_emu.py
```

Une fenêtre 512×256 (128×64 × 4) s'ouvre, affichant BPM, mode, step et macros.

### Étape 3 — Lancer la façade graphique

```bash
python sim/fake_panel.py --octatrack
```

Une fenêtre 900×500 affiche 12 encodeurs, 8 boutons et la scène Octatrack courante (OLED mock).

### Étape 4 — Lancer le séquenceur

```bash
python sim/sequencer.py
```

Le séquenceur envoie des triggers OSC vers Pure Data toutes les doubles-croches (BPM 128, 8 pistes Octatrack).

### Étape 5 — Lancer la génération IA (optionnel)

```bash
python sim/ai_gen.py
```

Un nouveau pattern kick est généré et envoyé toutes les 8 secondes.

### Étape 6 — Lancer le mode tracker (optionnel, alternatif au séquenceur)

```bash
python sim/tracker_mode.py --pattern tracker_pattern.json
```

Au premier lancement, crée `tracker_pattern.json` avec un pattern par défaut.

---

## 🚀 Lancement en une commande

```bash
# Terminal 1 : Pure Data (active le DSP !)
pd pd_patches/synth_octatrack.pd

# Terminal 2 : Stack Python complète
bash scripts/run_sim.sh
```

---

## 🎮 Interagir avec la simulation

### Contrôles `fake_panel.py --octatrack`

| Action | Effet |
|---|---|
| **Molette souris** | Modifier la valeur de l'encodeur sélectionné (0..127) |
| **Q** | Encodeur précédent |
| **W** | Encodeur suivant |
| **1..8** | Toggle boutons PAD (REC/PLAY/STOP/P1-P4/MODE) |
| **P1 (4)** | Scène A |
| **P2 (5)** | Scène B |
| **P3 (6)** | Morph A↔B |
| **ENC 11 + molette** | Crossfader `/oct/scene` |
| **Tenir 1-8 + molette** | P-lock sur le step |
| **Échap** | Quitter |

### Vérifier que les OSC arrivent dans Pure Data

Dans Pd, ouvrez une console (Window → Pd Window). Vous devriez voir les messages OSC apparaître.

---

## 🔍 Tester chaque composant isolément

```bash
# Tester seulement le séquenceur (sans Pure Data)
python sim/sequencer.py --bpm 100

# Tester seulement l'IA Markov
python sim/ai_gen.py

# Tester seulement le tracker
python sim/tracker_mode.py

# Tester les imports Python
python -c "from sim.osc_bridge import make_pd_client; print('OK')"
```

---

## 🛠️ Troubleshooting

| Symptôme | Cause probable | Solution |
|---|---|---|
| Aucun son dans Pure Data | DSP non activé | Menu **Media → DSP** dans Pd, ou **Ctrl+/** |
| `OSError: [Errno 98] Address already in use` sur port 5005 | Un process Pd ou Python utilise déjà le port | `lsof -i :5005` puis `kill <PID>` |
| `ModuleNotFoundError: No module named 'pygame'` | Venv non activé | `source venv/bin/activate` |
| Fenêtre PyGame ne s'ouvre pas | SDL2 manquant | `sudo apt install libsdl2-dev` (Linux) |
| Xruns / craquements audio | Buffer trop petit | Dans Pd : **Media → Audio Settings → Buffer size → 256** |
| `ModuleNotFoundError: No module named 'luma'` | luma non installé | `pip install luma.emulator luma.oled` |
| `tracker_pattern.json` corrompu | Édition manuelle avec erreur JSON | Supprimer le fichier, il sera recréé au prochain lancement |
| Pure Data : "oscparse : no such object" | Dépendance externe manquante | Vérifier que `oscparse` est bien dans Pd vanilla (inclus depuis 0.54) |

---

## 🎯 Latence cible

| Paramètre | Valeur cible |
|---|---|
| Latence audio totale | < 10 ms |
| Sample rate | 48 kHz |
| Buffer audio | 128 frames (PC) / 64 frames (RPi 5) |
| Latence OSC (localhost) | < 1 ms |

Pour atteindre < 10 ms à 48 kHz, configurez le buffer à **128 frames** dans Pure Data (Media → Audio Settings).

Sur Linux, des gains supplémentaires sont possibles avec :
```bash
# Priorité temps-réel pour Pd (nécessite JACK ou RTKit)
sudo sysctl -w kernel.sched_rt_runtime_us=-1
```
