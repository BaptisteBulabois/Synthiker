"""
fake_panel.py — Façade virtuelle Synthiker (12 encodeurs + 8 boutons + OLED mock).

Contrôles :
  Molette souris  → inc/déc valeur encodeur sélectionné (0..127)
  Q               → encodeur précédent
  W               → encodeur suivant
  1..8            → boutons PAD
  Échap           → quitter

Chaque changement envoie un message OSC vers Pure Data (port 5005).
"""

import sys
import math
import pygame
from pygame.math import Vector2

# Ajouter le répertoire racine au path pour les imports relatifs
sys.path.insert(0, __file__.replace("/sim/fake_panel.py", ""))

from sim.osc_bridge import (
    make_pd_client, make_oled_client,
    ADDR_ENC, ADDR_BTN, ADDR_MACRO
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


def draw_oled_mock(surface: pygame.Surface, enc_values: list[int]) -> None:
    """Dessine la zone OLED mock en haut de la fenêtre."""
    pygame.draw.rect(surface, (10, 10, 14), (0, 0, WIN_W, OLED_H))
    font = pygame.font.SysFont("monospace", 14)
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
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Synthiker — Fake Panel")
    clock = pygame.time.Clock()

    pd_client = make_pd_client()
    oled_client = make_oled_client()

    # État interne
    enc_values = [64] * 12   # 12 encodeurs, valeur initiale 64 (milieu)
    btn_states = [False] * 8  # 8 boutons
    selected_enc = 0

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

    running = True
    while running:
        clock.tick(FPS)

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
                    # Touches 1..8 → boutons
                    for i, k in enumerate([
                        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                        pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
                    ]):
                        if event.key == k:
                            btn_states[i] = not btn_states[i]
                            val = 1 if btn_states[i] else 0
                            pd_client.send_message(ADDR_BTN.format(i), val)
                            oled_client.send_message(ADDR_BTN.format(i), val)
                            print(f"[BTN] {BUTTON_LABELS[i]} → {val}")

            elif event.type == pygame.MOUSEWHEEL:
                # Molette : inc/déc l'encodeur sélectionné
                delta = event.y
                enc_values[selected_enc] = max(0, min(127, enc_values[selected_enc] + delta))
                v = enc_values[selected_enc]
                pd_client.send_message(ADDR_ENC.format(selected_enc), v)
                # Macros (encodeurs 9-11) → adresse /macro/
                if selected_enc >= 9:
                    macro_idx = selected_enc - 8  # 1..3
                    oled_client.send_message(ADDR_MACRO.format(macro_idx), v / 127.0)
                print(f"[ENC] {ENCODER_LABELS[selected_enc]} ({selected_enc}) → {v}")

        # --- Dessin ---
        screen.fill(BG_COLOR)
        draw_oled_mock(screen, enc_values)

        for i, (cx, cy) in enumerate(enc_positions):
            draw_encoder(screen, cx, cy, enc_values[i],
                         ENCODER_LABELS[i], i == selected_enc)

        for i, rect in enumerate(btn_positions):
            draw_button(screen, rect, BUTTON_LABELS[i], btn_states[i])

        # Indicateur encodeur sélectionné
        font_info = pygame.font.SysFont("monospace", 13)
        info = font_info.render(
            f"Encodeur sélectionné : {ENCODER_LABELS[selected_enc]} "
            f"(Q/W pour changer, molette pour régler)",
            True, (120, 120, 140)
        )
        screen.blit(info, (10, WIN_H - BTN_H - 42))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
