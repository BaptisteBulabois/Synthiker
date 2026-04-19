# Protocole OSC — Synthiker

## Réseau

| Paramètre | Valeur |
|---|---|
| IP | `127.0.0.1` (localhost) |
| Port Pd (récepteur audio) | `5005` |
| Port OLED (récepteur affichage) | `5006` |
| Protocole | UDP / OSC binaire (RFC OSC 1.1) |

---

## Tableau des adresses OSC

| Adresse | Arguments | Range | Description | Émetteur | Récepteur |
|---|---|---|---|---|---|
| `/enc/0` | `int` | 0..127 | Encodeur 0 — OSC pitch (fréquence oscillateur) | `fake_panel.py` | Pure Data |
| `/enc/1` | `int` | 0..127 | Encodeur 1 — PITCH (détune fin) | `fake_panel.py` | Pure Data |
| `/enc/2` | `int` | 0..127 | Encodeur 2 — WAVE (forme d'onde) | `fake_panel.py` | Pure Data |
| `/enc/3` | `int` | 0..127 | Encodeur 3 — CUT (fréquence de coupure filtre) | `fake_panel.py` | Pure Data |
| `/enc/4` | `int` | 0..127 | Encodeur 4 — RES (résonance filtre) | `fake_panel.py` | Pure Data |
| `/enc/5` | `int` | 0..127 | Encodeur 5 — ENV-A (attaque enveloppe, ms) | `fake_panel.py` | Pure Data |
| `/enc/6` | `int` | 0..127 | Encodeur 6 — ENV-D (decay enveloppe, ms) | `fake_panel.py` | Pure Data |
| `/enc/7` | `int` | 0..127 | Encodeur 7 — ENV-S (sustain enveloppe, 0..1) | `fake_panel.py` | Pure Data |
| `/enc/8` | `int` | 0..127 | Encodeur 8 — ENV-R (release enveloppe, ms) | `fake_panel.py` | Pure Data |
| `/enc/9` | `int` | 0..127 | Encodeur 9 — Macro M1 (Brightness) | `fake_panel.py` | Pure Data + OLED |
| `/enc/10` | `int` | 0..127 | Encodeur 10 — Macro M2 (Movement) | `fake_panel.py` | Pure Data + OLED |
| `/enc/11` | `int` | 0..127 | Encodeur 11 — Macro M3 (Density) | `fake_panel.py` | Pure Data + OLED |
| `/btn/0` | `int` | 0\|1 | Bouton REC — record | `fake_panel.py` | Pure Data |
| `/btn/1` | `int` | 0\|1 | Bouton PLAY — lecture | `fake_panel.py` | Pure Data |
| `/btn/2` | `int` | 0\|1 | Bouton STOP — arrêt | `fake_panel.py` | Pure Data |
| `/btn/3` | `int` | 0\|1 | Bouton P1 — pattern 1 | `fake_panel.py` | Pure Data |
| `/btn/4` | `int` | 0\|1 | Bouton P2 — pattern 2 | `fake_panel.py` | Pure Data |
| `/btn/5` | `int` | 0\|1 | Bouton P3 — pattern 3 | `fake_panel.py` | Pure Data |
| `/btn/6` | `int` | 0\|1 | Bouton P4 — pattern 4 | `fake_panel.py` | Pure Data |
| `/btn/7` | `int` | 0\|1 | Bouton MODE — changer de mode | `fake_panel.py` | Pure Data + OLED |
| `/note` | `int int int` | pitch(0..127) vel(0..127) track(0..3) | Trigger de note MIDI | `tracker_mode.py` | Pure Data |
| `/macro/1` | `float` | 0.0..1.0 | Macro 1 — Brightness | `fake_panel.py` | OLED |
| `/macro/2` | `float` | 0.0..1.0 | Macro 2 — Movement | `fake_panel.py` | OLED |
| `/macro/3` | `float` | 0.0..1.0 | Macro 3 — Density | `fake_panel.py` | OLED |
| `/macro/4` | `float` | 0.0..1.0 | Macro 4 — Chaos | `fake_panel.py` | OLED |
| `/seq/step` | `int` | 0..15 | Step courant du séquenceur | `sequencer.py` | Pure Data + OLED |
| `/seq/trig/0` | `int` | 0\|1 | Trigger piste 0 (kick) | `sequencer.py` | Pure Data |
| `/seq/trig/1` | `int` | 0\|1 | Trigger piste 1 (snare) | `sequencer.py` | Pure Data |
| `/seq/trig/2` | `int` | 0\|1 | Trigger piste 2 (hat) | `sequencer.py` | Pure Data |
| `/seq/trig/3` | `int` | 0\|1 | Trigger piste 3 (perc) | `sequencer.py` | Pure Data |
| `/seq/kick/0..15` | `int` | 0\|1 | Pattern kick généré par IA (step 0..15) | `ai_gen.py` | Pure Data |
| `/mode` | `string` | "step"\|"tracker" | Mode actuel du séquenceur | `tracker_mode.py` | OLED |
| `/heartbeat` | _(aucun)_ | — | Ping de vie | tous | OLED |
| `/bpm` | `int` | 60..300 | Tempo en BPM | `sequencer.py` | OLED |

---

## Conventions

### Encodeurs (0..127)

Les encodeurs envoient des entiers `int` de 0 à 127 (convention MIDI CC).  
La conversion en paramètre physique est effectuée **dans Pure Data** :

```
pitch  : 0..127 → 100..500 Hz   (via expr)
cutoff : 0..127 → 200..5000 Hz  (via expr)
amp    : 0..127 → 0.0..1.0      (via expr)
```

### Boutons (0|1)

Envoi de `1` à l'appui, `0` au relâchement.

### Notes (`/note pitch vel track`)

Format identique au MIDI : pitch 60 = Do central (C4), velocity 0..127.

---

## Extensibilité

Pour ajouter un nouveau paramètre OSC :

1. **Ajouter la constante** dans `sim/osc_bridge.py` (`ADDR_xxx = "/xxx/{}"`).
2. **Émettre** le message depuis le module Python concerné via `client.send_message(ADDR_xxx.format(idx), val)`.
3. **Réceptionner** dans `pd_patches/synth_main.pd` : ajouter le chemin dans `[route ...]` et connecter les outlets.
