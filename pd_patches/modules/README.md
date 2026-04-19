# Modules Pd Avancés — Placeholder (PR #3)

Ce dossier accueillera les **12 modules Pure Data avancés** qui seront développés dans la PR #3.

## 📋 Liste des modules prévus

| Module | Description |
|---|---|
| `fm_wavetable.pd` | Synthèse FM + wavetable (4 opérateurs, 8 algorithmes) |
| `granular.pd` | Synthèse granulaire (taille de grain, densité, pitch) |
| `vocoder_fft.pd` | Vocoder FFT 32 bandes |
| `sample_looper.pd` | Sample looper avec time-stretch (phase vocoder simplifié) |
| `reverb_schroeder.pd` | Réverb Schroeder (4 combs + 2 allpass) |
| `delay_multitap.pd` | Delay modulé multi-tap (sync BPM) |
| `distortion_bitcrush.pd` | Distortion / bitcrusher / saturation |
| `pitch_shifter.pd` | Pitch shifter par phase vocoder |
| `arpeggiator.pd` | Arpégiateur polyrythmique (modes up/down/random/chord) |
| `master_bus.pd` | Bus master : compresseur + EQ 3 bandes + limiteur |
| `macros.pd` | 4 Macros : Brightness / Movement / Density / Chaos |
| `mixer.pd` | Mixeur 4 pistes stéréo avec send/return |

## 🔌 Interface commune (convention PR #3)

Chaque module exposera :
- **Entrée OSC** : `/module/<nom>/<paramètre> <valeur>` sur port 5005
- **Signaux** : inlet gauche = signal audio in, inlet droit = signal auxiliaire
- **Outlet** : signal audio out (stéréo pour modules stéréo)

## ⏳ Statut

En attente de la **PR #1** (simu PC) et de la **PR #2** (firmware RPi 5).

> Ne pas développer ces modules avant d'avoir validé le pipeline OSC de la PR #1 sur PC.
