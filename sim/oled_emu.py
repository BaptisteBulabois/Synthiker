"""
oled_emu.py — Émulateur OLED 128×64 via luma.emulator pour Synthiker.

Écoute les messages OSC sur le port 5006 et met à jour l'affichage.

Pour passer au vrai OLED SSD1306 sur Raspberry Pi, remplacez simplement :
    from luma.emulator.device import pygame as oled_device
par :
    from luma.oled.device import ssd1306 as oled_device
et adaptez la création du device (I2C bus + adresse).

Usage :
    python sim/oled_emu.py
"""

import sys
import threading
import time

from luma.core.render import canvas
from luma.emulator.device import pygame as oled_device
from PIL import ImageFont

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

sys.path.insert(0, __file__.replace("/sim/oled_emu.py", ""))

from sim.osc_bridge import OSC_PORT_OLED

# ---------------------------------------------------------------------------
# État de l'écran (mis à jour par les callbacks OSC)
# ---------------------------------------------------------------------------
_state: dict = {
    "bpm": 120,
    "mode": "step",
    "pattern": 0,
    "last_macro": ("M1", 0.5),
}
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Callbacks OSC
# ---------------------------------------------------------------------------

def _on_bpm(addr: str, *args) -> None:
    with _lock:
        _state["bpm"] = int(args[0]) if args else _state["bpm"]


def _on_mode(addr: str, *args) -> None:
    with _lock:
        _state["mode"] = str(args[0]) if args else _state["mode"]


def _on_seq_step(addr: str, *args) -> None:
    with _lock:
        _state["pattern"] = int(args[0]) if args else _state["pattern"]


def _on_macro(addr: str, *args) -> None:
    # addr = "/macro/1", "/macro/2", ...
    idx = addr.split("/")[-1]
    val = float(args[0]) if args else 0.0
    with _lock:
        _state["last_macro"] = (f"M{idx}", val)


def _on_heartbeat(addr: str, *args) -> None:
    pass  # juste un ping de vie, pas besoin de l'afficher


def build_dispatcher() -> Dispatcher:
    """Crée et configure le dispatcher OSC."""
    d = Dispatcher()
    d.map("/bpm", _on_bpm)
    d.map("/mode", _on_mode)
    d.map("/seq/step", _on_seq_step)
    d.map("/macro/*", _on_macro)
    d.map("/heartbeat", _on_heartbeat)
    return d


# ---------------------------------------------------------------------------
# Rendu OLED
# ---------------------------------------------------------------------------

def render_oled(device) -> None:
    """Boucle de rendu : redessine l'écran OLED à ~10 FPS."""
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    while True:
        with _lock:
            bpm = _state["bpm"]
            mode = _state["mode"]
            pattern = _state["pattern"]
            macro_name, macro_val = _state["last_macro"]

        with canvas(device) as draw:
            # Titre
            draw.text((0, 0),  "[ SYNTHIKER ]", fill="white", font=font)
            # BPM
            draw.text((0, 14), f"BPM : {bpm}", fill="white", font=font)
            # Mode
            draw.text((0, 26), f"Mode: {mode}", fill="white", font=font)
            # Step courant
            draw.text((0, 38), f"Step: {pattern:02d}/15", fill="white", font=font)
            # Dernière macro
            bar_w = int(macro_val * 80)
            draw.text((0, 50), f"{macro_name}:", fill="white", font=font)
            draw.rectangle([24, 52, 24 + 80, 62], outline="white")
            if bar_w > 0:
                draw.rectangle([24, 52, 24 + bar_w, 62], fill="white")

        time.sleep(0.1)


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> None:
    """Lance le serveur OSC et la boucle de rendu OLED."""
    # Créer le device (fenêtre 128×64 scalée ×4)
    device = oled_device(width=128, height=64, scale=4, mode="1")

    # Serveur OSC dans un thread dédié
    dispatcher = build_dispatcher()
    server = ThreadingOSCUDPServer(("127.0.0.1", OSC_PORT_OLED), dispatcher)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[OLED] Serveur OSC en écoute sur port {OSC_PORT_OLED}")
    print("[OLED] Ctrl+C pour arrêter")

    try:
        render_oled(device)
    except KeyboardInterrupt:
        print("\n[OLED] Arrêt propre.")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
