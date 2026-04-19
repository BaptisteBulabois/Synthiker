# Roadmap — Synthiker

> **Ne rien acheter avant d'avoir validé la simulation PC (PR #1) !**

---

## Phase 1 — Simulateur PC ✅ (PR #1)

**Objectif** : valider le pipeline complet (UI → OSC → audio → IA) sur n'importe quel PC avant d'investir dans le hardware.

**Livraisons** :
- `sim/fake_panel.py` — interface graphique PyGame (12 encodeurs + 8 boutons)
- `sim/sequencer.py` — séquenceur 16 pas → OSC
- `sim/tracker_mode.py` — mode tracker JSON → OSC
- `sim/ai_gen.py` — génération Markov → OSC
- `sim/oled_emu.py` — émulateur OLED 128×64
- `pd_patches/synth_main.pd` — patch Pure Data vanilla (osc~ + lop~ + enveloppe)
- Documentation complète (protocole OSC, guide simulation, roadmap)

**Critères d'acceptation** :
- `python sim/fake_panel.py` → fenêtre PyGame sans crash
- `python sim/sequencer.py` → OSC envoyés en boucle
- `pd_patches/synth_main.pd` → s'ouvre dans Pd vanilla sans erreur
- Tourner un encodeur dans fake_panel → changement audible dans Pd

---

## Phase 2 — Firmware Raspberry Pi 5 ⏳ (PR #2)

**Objectif** : déployer le même code Python sur le Raspberry Pi 5 avec les GPIOs réels.

**Livraisons prévues** :
- `gpio_control.py` — lecture encodeurs EC11 + boutons via MCP23017 + PCA9685
- `systemd/` — services `synthiker-panel.service`, `synthiker-seq.service`, `synthiker-oled.service`
- `scripts/install.sh` — installation complète RPi (venv, systemd, Pure Data)
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
- MCP23017 (GPIO expander I²C) + PCA9685 (PWM) — ~7€

---

## Phase 3 — Modules Pd Avancés + Magenta IA ⏳ (PR #3)

**Objectif** : enrichir le moteur audio et remplacer la chaîne Markov par un vrai modèle de génération musicale.

**12 modules Pure Data** (voir `pd_patches/modules/README.md`) :

| Module | Technique |
|---|---|
| FM Wavetable | 4 opérateurs, 8 algorithmes FM |
| Granular | Grain size, density, pitch scatter |
| Vocoder FFT | 32 bandes, analyse/synthèse |
| Sample Looper | Time-stretch (phase vocoder) |
| Reverb Schroeder | 4 combs + 2 allpass |
| Delay Multi-tap | Sync BPM, modulation LFO |
| Distortion/Bitcrush | Saturation, bit depth, sample rate |
| Pitch Shifter | Phase vocoder temps-réel |
| Arpégiateur | Polyrythmique, modes up/down/random/chord |
| Master Bus | Compresseur + EQ 3 bandes + limiteur |
| 4 Macros | Brightness / Movement / Density / Chaos |
| Mixeur | 4 pistes stéréo, send/return |

**IA Magenta** :
- Remplacement de `ai_gen.py` (Markov) par MusicVAE / GrooVAE de Google Magenta
- GPU recommandé (ou TPU Coral pour le Pi)
- API identique → zéro changement côté OSC

---

## Phase 4 — Hardware Final ⏳ (PR #4)

**Objectif** : produire un boîtier physique fini avec PCB dédié.

**Livraisons prévues** :
- `hardware/kicad/` — schéma + PCB KiCAD (Gerbers prêts pour JLCPCB)
- `hardware/stl/` — boîtier PETG (impression 3D) + façade aluminium (découpe laser)
- `hardware/bom.csv` — Bill of Materials complet

### BOM indicatif

| Composant | Prix indicatif |
|---|---|
| Raspberry Pi 5 (8 Go) | ~95€ |
| HiFiBerry DAC2 Pro | ~45€ |
| Afficheur OLED 2.42" SSD1306 | ~18€ |
| 12 encodeurs rotatifs Alps EC11 | ~30€ |
| 8 switches LED tactiles | ~8€ |
| MCP23017 + PCA9685 | ~7€ |
| Boîtier PETG + façade alu | ~70€ |
| Divers (câbles, PCB, visserie) | ~50€ |
| **Total estimé** | **~323–540€** |

> Les fourchettes de prix varient selon la source (AliExpress vs distributeur européen).

---

## Calendrier prévisionnel

```
PR #1 ✅  →  PR #2 (3-4 sem.)  →  PR #3 (4-6 sem.)  →  PR #4 (2-3 mois)
```

*Les délais dépendent de la disponibilité et des retours de la communauté.*
