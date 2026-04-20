"""
fake_panel.py — Façade virtuelle Synthiker (12 encodeurs + 8 boutons + OLED mock).

Contrôles :
  Molette souris  → inc/déc valeur encodeur sélectionné (0..127)
  Q               → encodeur précédent
  W               → encodeur suivant
  1..8            → boutons PAD
  Échap           → quitter

Mode Octatrack (--octatrack) :
  P1 (touche 4)   → applique Scène A (encode defaults A)
  P2 (touche 5)   → applique Scène B (encode defaults B)
  P3 (touche 6)   → morphing progressif entre scène courante et l'autre
  P4 (touche 7)   → cycle parmi les patterns disponibles (affichage console)
  MODE (touche 8) → bascule affichage OLED (scène / step info)
  ENC 11 (M3)     → crossfader /oct/scene (0=A, 127=B)
  Tenir 1..8 + molette → enregistre un P-lock sur le step correspondant

Chaque changement envoie un message OSC vers Pure Data (port 5005).
"""

import argparse
import sys
import math
import pygame
from pygame.math import Vector2

# Ajouter le répertoire racine au path pour les imports relatifs
sys.path.insert(0, __file__.replace("/sim/fake_panel.py", ""))

from sim.osc_bridge import (
    make_pd_client, make_oled_client,
    ADDR_ENC, ADDR_BTN, ADDR_MACRO, ADDR_OCT_SCENE
)
from sim.presets.octatrack import (
    ENCODER_DEFAULTS_A, ENCODER_DEFAULTS_B,
    PATTERNS, PATTERNS_LIVE, PATTERNS_SCENE_B,
)

# ---------------------------------------------------------------------------
# Constantes UI
# ---------------------------------------------------------------------------
WIN_W, WIN_H = 900, 500
FPS = 60
BG_COLOR = (18, 18, 24)
ENC_RADIUS = 28
ENC_COLS = 6
ENCODER_COLOR = (60, 60, 80)
NEEDLE_COLOR = (220, 180, 50)
NEEDLE_OFFSET = 4   # distance en pixels entre le bord du cercle et la pointe de l'aiguille
SEL_COLOR = (80, 200, 120)
BTN_W, BTN_H = 80, 36
BTN_COLOR = (50, 50, 70)
BTN_ACTIVE_COLOR = (200, 80, 60)
TEXT_COLOR = (200, 200, 200)
OLED_H = 60  # hauteur de la zone OLED mock en haut

ENCODER_LABELS = [
    "OSC", "PITCH", "WAVE",
    "CUT", "RES", "ENV-A",
    "ENV-D", "ENV-S", "ENV-R",
    "M1", "M2", "M3",
]

BUTTON_LABELS = ["REC", "PLAY", "STOP", "P1", "P2", "P3", "P4", "MODE"]

# Octatrack mode constants
_OCT_PATTERN_NAMES = ["default", "live", "scene_b"]
_OCT_PATTERNS = [PATTERNS, PATTERNS_LIVE, PATTERNS_SCENE_B]
_OCT_BTN_P1 = 3   # index in btn_states for P1
_OCT_BTN_P2 = 4   # P2
_OCT_BTN_P3 = 5   # P3
_OCT_BTN_P4 = 6   # P4
_OCT_BTN_MODE = 7  # MODE
_OCT_ENC_XFADE = 11  # M3 encoder = crossfader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def val_to_angle(value: int) -> float:
    """Convertit une valeur 0..127 en angle (radians) pour l'aiguille.

    0   → -135° (en bas à gauche)
    127 → +135° (en bas à droite)
    """
    return math.radians(-135 + (value / 127.0) * 270)


def draw_encoder(surface: pygame.Surface, cx: int, cy: int,
                 value: int, label: str, selected: bool) -> None:
    """Dessine un encodeur rotatif avec aiguille et label."""
    color = SEL_COLOR if selected else ENCODER_COLOR
    pygame.draw.circle(surface, color, (cx, cy), ENC_RADIUS, 2)

    # Aiguille
    angle = val_to_angle(value)
    tip = Vector2(cx, cy) + Vector2(math.sin(angle), -math.cos(angle)) * (ENC_RADIUS - NEEDLE_OFFSET)
    pygame.draw.line(surface, NEEDLE_COLOR, (cx, cy), (int(tip.x), int(tip.y)), 3)

    # Valeur numérique
    font_small = pygame.font.SysFont("monospace", 11)
    val_surf = font_small.render(str(value), True, TEXT_COLOR)
    surface.blit(val_surf, val_surf.get_rect(center=(cx, cy + ENC_RADIUS + 10)))

    # Label
    label_surf = font_small.render(label, True, TEXT_COLOR)
    surface.blit(label_surf, label_surf.get_rect(center=(cx, cy + ENC_RADIUS + 22)))


def draw_button(surface: pygame.Surface, rect: pygame.Rect,
                label: str, active: bool) -> None:
    """Dessine un bouton PAD."""
    color = BTN_ACTIVE_COLOR if active else BTN_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=4)
    pygame.draw.rect(surface, (100, 100, 120), rect, 1, border_radius=4)
    font = pygame.font.SysFont("monospace", 12)
    surf = font.render(label, True, TEXT_COLOR)
    surface.blit(surf, surf.get_rect(center=rect.center))


def draw_oled_mock(surface: pygame.Surface, enc_values: list[int],
                   oct_mode: bool = False, oct_scene_label: str = "A",
                   oct_xfade: float = 0.0, oct_oled_mode: str = "scene",
                   oct_pattern_name: str = "default") -> None:
    """Dessine la zone OLED mock en haut de la fenêtre."""
    pygame.draw.rect(surface, (10, 10, 14), (0, 0, WIN_W, OLED_H))
    font = pygame.font.SysFont("monospace", 14)

    if oct_mode and oct_oled_mode == "scene":
        title = font.render(f"[ OCTATRACK — SCENE {oct_scene_label} ]", True, (100, 200, 240))
        surface.blit(title, (10, 8))
        # Crossfader bar
        bar_x, bar_y, bar_w = 10, 32, 200
        pygame.draw.rect(surface, (40, 40, 50), (bar_x, bar_y, bar_w, 10))
        fill_w = int(oct_xfade * bar_w)
        bar_color = (100, 200, 140) if oct_xfade < 0.5 else (200, 120, 60)
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, 10))
        xf_lbl = font.render(f"A←{int(oct_xfade*100):3d}%→B  pat:{oct_pattern_name}",
                             True, (180, 180, 180))
        surface.blit(xf_lbl, (220, 28))
    else:
        title = font.render("[ SYNTHIKER ]", True, (100, 240, 160))
        surface.blit(title, (10, 8))
        # Affiche macros M1-M3 (encodeurs 9-11)
        macro_labels = ["M1", "M2", "M3"]
        for i, (lbl, idx) in enumerate(zip(macro_labels, [9, 10, 11])):
            pct = enc_values[idx] / 127.0
            bar_w = int(pct * 100)
            bx = 200 + i * 160
            pygame.draw.rect(surface, (40, 40, 50), (bx, 15, 100, 12))
            pygame.draw.rect(surface, (100, 200, 140), (bx, 15, bar_w, 12))
            lbl_surf = font.render(f"{lbl}:{enc_values[idx]:3d}", True, TEXT_COLOR)
            surface.blit(lbl_surf, (bx + 105, 12))

    # Séparateur
    pygame.draw.line(surface, (50, 50, 60), (0, OLED_H - 1), (WIN_W, OLED_H - 1))


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

def main() -> None:
    """Point d'entrée : lance la fenêtre fake_panel."""
    parser = argparse.ArgumentParser(description="Synthiker — Fake Panel")
    parser.add_argument(
        "--octatrack", action="store_true",
        help="Active le mode Octatrack (scènes A/B, crossfader, p-locks)",
    )
    args = parser.parse_args()
    oct_mode: bool = args.octatrack

    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    caption = "Synthiker — Fake Panel [OCTATRACK]" if oct_mode else "Synthiker — Fake Panel"
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()

    pd_client = make_pd_client()
    oled_client = make_oled_client()

    # État interne
    enc_values = [64] * 12   # 12 encodeurs, valeur initiale 64 (milieu)
    btn_states = [False] * 8  # 8 boutons
    selected_enc = 0

    # --- État Octatrack ---
    oct_scene_label: str = "A"        # scène courante affichée
    oct_scene_src: list[int] = list(ENCODER_DEFAULTS_A)   # valeurs de départ du morph
    oct_scene_dst: list[int] = list(ENCODER_DEFAULTS_B)   # valeurs cible du morph
    oct_morph_step: int = 0           # 0 = pas de morph en cours
    OCT_MORPH_STEPS: int = 20         # nombre d'étapes pour le morph progressif
    oct_oled_mode: str = "scene"      # "scene" ou "info"
    oct_pattern_idx: int = 0          # index du pattern courant
    # P-locks : {step (0-7): {enc_idx: value}}
    oct_plocks: dict[int, dict[int, int]] = {}
    oct_morph_dst_label: str = "B"    # label de la scène cible (mis à jour au lancement du morph)

    if oct_mode:
        # Initialise les encodeurs sur les valeurs de la Scène A
        enc_values = list(ENCODER_DEFAULTS_A)
        for idx, val in enumerate(enc_values):
            pd_client.send_message(ADDR_ENC.format(idx), val)
        print("[OCT] Mode Octatrack actif — Scène A chargée")
        print("[OCT] P1=ScèneA  P2=ScèneB  P3=Morph  P4=PatternSuivant")
        print("[OCT] ENC11=Crossfader  Tenir 1-8 + molette = P-lock")

    # Calcul positions encodeurs (2 rangées × 6 colonnes)
    enc_positions = []
    start_x = 80
    start_y = OLED_H + 60
    spacing_x = (WIN_W - 2 * start_x) // (ENC_COLS - 1)
    for row in range(2):
        for col in range(ENC_COLS):
            enc_positions.append((start_x + col * spacing_x, start_y + row * 100))

    # Positions boutons (rangée du bas)
    btn_y = WIN_H - BTN_H - 20
    btn_positions = []
    total_btn_w = 8 * BTN_W + 7 * 8
    bx = (WIN_W - total_btn_w) // 2
    for i in range(8):
        btn_positions.append(pygame.Rect(bx + i * (BTN_W + 8), btn_y, BTN_W, BTN_H))

    # Clés 1-8 mappées sur les pads
    _PAD_KEYS = [
        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
        pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
    ]

    def _send_scene(defaults: list[int], label: str) -> None:
        """Envoie un jeu de valeurs d'encodeurs et met à jour l'état local."""
        nonlocal oct_scene_label
        oct_scene_label = label
        for idx, val in enumerate(defaults):
            enc_values[idx] = val
            pd_client.send_message(ADDR_ENC.format(idx), val)
            if idx >= 9:
                oled_client.send_message(ADDR_MACRO.format(idx - 8), val / 127.0)
        print(f"[OCT] Scène {label} appliquée")

    running = True
    while running:
        clock.tick(FPS)

        # Morph progressif Octatrack (P3)
        if oct_mode and oct_morph_step > 0:
            t = 1.0 - oct_morph_step / OCT_MORPH_STEPS
            for idx in range(12):
                a = oct_scene_src[idx]
                b = oct_scene_dst[idx]
                val = int(a + (b - a) * t)
                enc_values[idx] = val
                pd_client.send_message(ADDR_ENC.format(idx), val)
            oct_morph_step -= 1
            if oct_morph_step == 0:
                # Morph terminé : fixe les valeurs finales et met à jour le label de scène
                enc_values[:] = list(oct_scene_dst)
                oct_scene_label = oct_morph_dst_label
                print(f"[OCT] Morph terminé → Scène {oct_scene_label}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_q:
                    selected_enc = (selected_enc - 1) % 12
                elif event.key == pygame.K_w:
                    selected_enc = (selected_enc + 1) % 12
                else:
                    for i, k in enumerate(_PAD_KEYS):
                        if event.key == k:
                            if oct_mode:
                                if i == _OCT_BTN_P1:
                                    # P1 → Scène A
                                    _send_scene(ENCODER_DEFAULTS_A, "A")
                                elif i == _OCT_BTN_P2:
                                    # P2 → Scène B
                                    _send_scene(ENCODER_DEFAULTS_B, "B")
                                elif i == _OCT_BTN_P3:
                                    # P3 → Lancer morph vers l'autre scène
                                    if oct_scene_label == "A":
                                        oct_scene_src = list(enc_values)
                                        oct_scene_dst = list(ENCODER_DEFAULTS_B)
                                        oct_morph_dst_label = "B"
                                    else:
                                        oct_scene_src = list(enc_values)
                                        oct_scene_dst = list(ENCODER_DEFAULTS_A)
                                        oct_morph_dst_label = "A"
                                    oct_morph_step = OCT_MORPH_STEPS
                                    print(f"[OCT] Morph Scène {oct_scene_label} → "
                                          f"{oct_morph_dst_label} lancé")
                                elif i == _OCT_BTN_P4:
                                    # P4 → Pattern suivant
                                    oct_pattern_idx = (oct_pattern_idx + 1) % len(_OCT_PATTERN_NAMES)
                                    name = _OCT_PATTERN_NAMES[oct_pattern_idx]
                                    print(f"[OCT] Pattern → {name}  "
                                          f"(relance avec --design octatrack --pattern {name})")
                                elif i == _OCT_BTN_MODE:
                                    # MODE → bascule affichage OLED
                                    oct_oled_mode = "info" if oct_oled_mode == "scene" else "scene"
                                    print(f"[OCT] OLED mode → {oct_oled_mode}")
                                else:
                                    # REC/PLAY/STOP : comportement normal
                                    btn_states[i] = not btn_states[i]
                                    val = 1 if btn_states[i] else 0
                                    pd_client.send_message(ADDR_BTN.format(i), val)
                                    oled_client.send_message(ADDR_BTN.format(i), val)
                                    print(f"[BTN] {BUTTON_LABELS[i]} → {val}")
                            else:
                                btn_states[i] = not btn_states[i]
                                val = 1 if btn_states[i] else 0
                                pd_client.send_message(ADDR_BTN.format(i), val)
                                oled_client.send_message(ADDR_BTN.format(i), val)
                                print(f"[BTN] {BUTTON_LABELS[i]} → {val}")

            elif event.type == pygame.MOUSEWHEEL:
                delta = event.y
                # En mode Octatrack, vérifier si une touche 1-8 est maintenue → P-lock
                if oct_mode:
                    keys = pygame.key.get_pressed()
                    held_step: int | None = None
                    for step_key_idx, k in enumerate(_PAD_KEYS):
                        if keys[k]:
                            held_step = step_key_idx  # step 0-7
                            break
                    if held_step is not None:
                        enc_values[selected_enc] = max(
                            0, min(127, enc_values[selected_enc] + delta)
                        )
                        v = enc_values[selected_enc]
                        if held_step not in oct_plocks:
                            oct_plocks[held_step] = {}
                        oct_plocks[held_step][selected_enc] = v
                        plock_count = sum(len(d) for d in oct_plocks.values())
                        print(f"[PLOCK] step={held_step+1}  "
                              f"{ENCODER_LABELS[selected_enc]}={v}  "
                              f"(p-locks actifs: {plock_count})")
                        continue  # pas d'envoi OSC normal pour un p-lock

                enc_values[selected_enc] = max(0, min(127, enc_values[selected_enc] + delta))
                v = enc_values[selected_enc]
                pd_client.send_message(ADDR_ENC.format(selected_enc), v)
                # Macros (encodeurs 9-11) → adresse /macro/
                if selected_enc >= 9:
                    macro_idx = selected_enc - 8  # 1..3
                    oled_client.send_message(ADDR_MACRO.format(macro_idx), v / 127.0)
                # Encodeur 11 en mode Octatrack → crossfader
                if oct_mode and selected_enc == _OCT_ENC_XFADE:
                    xfade_val = v / 127.0
                    pd_client.send_message(ADDR_OCT_SCENE, xfade_val)
                    print(f"[OCT] Crossfader /oct/scene → {xfade_val:.3f}")
                else:
                    print(f"[ENC] {ENCODER_LABELS[selected_enc]} ({selected_enc}) → {v}")

        # --- Dessin ---
        screen.fill(BG_COLOR)

        oct_xfade = enc_values[_OCT_ENC_XFADE] / 127.0 if oct_mode else 0.0
        draw_oled_mock(
            screen, enc_values,
            oct_mode=oct_mode,
            oct_scene_label=oct_scene_label,
            oct_xfade=oct_xfade,
            oct_oled_mode=oct_oled_mode,
            oct_pattern_name=_OCT_PATTERN_NAMES[oct_pattern_idx],
        )

        for i, (cx, cy) in enumerate(enc_positions):
            draw_encoder(screen, cx, cy, enc_values[i],
                         ENCODER_LABELS[i], i == selected_enc)

        for i, rect in enumerate(btn_positions):
            draw_button(screen, rect, BUTTON_LABELS[i], btn_states[i])

        # Indicateur encodeur sélectionné
        font_info = pygame.font.SysFont("monospace", 13)
        info_text = (
            f"Encodeur sélectionné : {ENCODER_LABELS[selected_enc]} "
            f"(Q/W pour changer, molette pour régler)"
        )
        if oct_mode:
            plock_count = sum(len(d) for d in oct_plocks.values())
            info_text += f"  |  P-locks: {plock_count}"
        info = font_info.render(info_text, True, (120, 120, 140))
        screen.blit(info, (10, WIN_H - BTN_H - 42))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
