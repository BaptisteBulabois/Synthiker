# Roadmap — Synthiker (design Octatrack)

> **Ne rien acheter avant d'avoir validé la simulation PC (PR #1) !**

---

## Phase 1 — Simulateur PC ✅ (PR #1)

**Objectif** : valider le pipeline complet (UI → OSC → audio → IA) sur n'importe quel PC avant d'investir dans le hardware.

**Livraisons** :
- `sim/fake_panel.py` — interface graphique PyGame (12 encodeurs + 8 boutons + mode Octatrack)
- `sim/sequencer.py` — séquenceur 16 pas 8 pistes → OSC (BPM 128, patterns Octatrack)
- `sim/design_selector.py` — CLI lanceur Octatrack (patterns default/live/scene_b, BPM)
- `sim/presets/octatrack.py` — patterns + scènes A/B + encodeurs
- `sim/tracker_mode.py` — mode tracker JSON → OSC
- `sim/ai_gen.py` — génération Markov → OSC
- `sim/oled_emu.py` — émulateur OLED 128×64
- `pd_patches/synth_octatrack.pd` — patch Pure Data 8 pistes (BD/SD/HH/CL + BASS/LEAD/CHORD/FX)
- Documentation complète (protocole OSC, guide simulation, roadmap)

**Critères d'acceptation** :
- `python sim/fake_panel.py --octatrack` → fenêtre PyGame avec scènes A/B et crossfader
- `python sim/sequencer.py` → OSC 8 pistes envoyés en boucle à BPM 128
- `pd_patches/synth_octatrack.pd` → s'ouvre dans Pd vanilla sans erreur
- Tourner ENC11 dans fake_panel → envoi `/oct/scene` audible dans Pd

---

## Phase 2 — Firmware Raspberry Pi 5 ⏳ (PR #2)

**Objectif** : déployer le même code Python sur le Raspberry Pi 5 avec les GPIOs réels, configuré pour le design Octatrack (8 pistes, scènes A/B, crossfader physique).

**Livraisons prévues** :
- `gpio_control.py` — lecture 12 encodeurs EC11 + 8 boutons via MCP23017, P-locks hardware
- `gpio_crossfader.py` — lecture potentiomètre linéaire (crossfader A↔B) via ADC I²C → `/oct/scene`
- `gpio_oled.py` — affichage SSD1306 : scène courante, BPM, crossfader position, p-lock count
- `systemd/` — services `synthiker-panel.service`, `synthiker-seq.service`, `synthiker-oled.service`
- `scripts/install.sh` — installation complète RPi (venv, systemd, Pure Data, patch octatrack)
- `scripts/tune_realtime.sh` — optimisation temps-réel (CPU governor, IRQ affinity, JACK)

**Compatibilité PC/RPi** :
```bash
# Tester le firmware RPi sur PC (sans GPIO réels)
GPIOZERO_PIN_FACTORY=mock python gpio_control.py
```
Grâce à `GPIOZERO_PIN_FACTORY=mock`, **le même code** tourne sur PC et sur Pi — zéro ligne de code jeté.

**Matériel nécessaire** :
- Raspberry Pi 5 (8 Go) — ~95€
- HiFiBerry DAC2 Pro (HAT I²S) — ~45€
- Afficheur OLED SSD1306 2.42" — ~18€
- 12 encodeurs rotatifs Alps EC11 — ~30€
- 8 switches LED tactiles — ~8€
- 1 potentiomètre linéaire 10 kΩ (crossfader A↔B) — ~3€
- MCP23017 (GPIO expander I²C) + ADS1115 (ADC 16 bits pour le crossfader) — ~9€

---

## Phase 3 — Modules Pd Octatrack + Magenta IA ⏳ (PR #3)

**Objectif** : enrichir le moteur audio Octatrack avec des modules Pd avancés adaptés aux 8 pistes, et remplacer la chaîne Markov par un vrai modèle IA de génération musicale.

**12 modules Pure Data ciblés Octatrack** :

| Module | Groupe | Technique |
|---|---|---|
| FM Wavetable (BD/LEAD) | Percussions + mélodie | 4 opérateurs, 8 algorithmes FM |
| Granular (FX) | Mélodie | Grain size, density, pitch scatter |
| Filtre résonant scène (CUT+RES) | Tous | VCF piloté par `/oct/scene` — interpole entre deux réglages |
| Reverb Schroeder (CHORD/FX) | Mélodie | 4 combs + 2 allpass |
| Delay Multi-tap (LEAD) | Mélodie | Sync BPM 128, modulation LFO |
| Distortion/Bitcrush (BD/SD) | Percussions | Saturation, bit depth, sample rate |
| Arpégiateur (BASS/CHORD) | Mélodie | Polyrythmique, modes up/down/random/chord |
| P-lock interpolation | Tous | Interpole en temps réel les p-locks actifs entre deux steps |
| Scene Morpher | Tous | Morphing A↔B géré côté Pd (reçoit `/oct/scene`) |
| Master Bus | Tous | Compresseur + EQ 3 bandes + limiteur |
| 4 Macros (M1-M4) | Tous | Brightness / Movement / Density / Chaos |
| Mixeur 8 pistes | Tous | 8 pistes stéréo, send/return |

**IA Magenta** :
- Remplacement de `ai_gen.py` (Markov) par **GrooVAE** de Google Magenta (groove generation 8 pistes)
- Le modèle génère des variations de patterns pour chaque piste Octatrack
- GPU recommandé (ou TPU Coral pour le Pi)
- API identique → zéro changement côté OSC

---

## Phase 4 — Hardware Final Octatrack ⏳ (PR #4)

**Objectif** : produire un boîtier physique fini inspiré de l'Octatrack, avec PCB dédié, crossfader physique et afficheur OLED de scène.

**Livraisons prévues** :
- `hardware/kicad/` — schéma + PCB KiCAD (Gerbers prêts pour JLCPCB)
  - 12 encodeurs EC11 + 8 switches LED + 1 potentiomètre crossfader
  - Connecteur OLED SSD1306 + connecteur HAT HiFiBerry
  - ADS1115 pour le crossfader analogique
- `hardware/stl/` — boîtier PETG (impression 3D) façon Octatrack : façade alu découpée laser
  - Sérigraphie : labels BD/SD/HH/CL + BASS/LEAD/CHORD/FX + SCENE A/B + XFADER
- `hardware/bom.csv` — Bill of Materials complet

### BOM indicatif

| Composant | Prix indicatif |
|---|---|
| Raspberry Pi 5 (8 Go) | ~95€ |
| HiFiBerry DAC2 Pro | ~45€ |
| Afficheur OLED 2.42" SSD1306 | ~18€ |
| 12 encodeurs rotatifs Alps EC11 | ~30€ |
| 8 switches LED tactiles | ~8€ |
| Potentiomètre linéaire 10 kΩ (crossfader) | ~3€ |
| MCP23017 + ADS1115 | ~9€ |
| Boîtier PETG + façade alu | ~70€ |
| Divers (câbles, PCB, visserie) | ~50€ |
| **Total estimé** | **~328–400€** |

> Les fourchettes de prix varient selon la source (AliExpress vs distributeur européen).

---

## Calendrier prévisionnel

```
PR #1 ✅  →  PR #2 (3-4 sem.)  →  PR #3 (4-6 sem.)  →  PR #4 (2-3 mois)
```

*Les délais dépendent de la disponibilité et des retours de la communauté.*
