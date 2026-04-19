"""OSC bridge - adresses et clients partagés pour la simu Synthiker."""

from pythonosc.udp_client import SimpleUDPClient

# ---------------------------------------------------------------------------
# Réseau
# ---------------------------------------------------------------------------
OSC_IP = "127.0.0.1"
OSC_PORT_PD = 5005    # Pure Data écoute ici
OSC_PORT_OLED = 5006  # Émulateur OLED écoute ici

# ---------------------------------------------------------------------------
# Adresses OSC
# ---------------------------------------------------------------------------
ADDR_ENC = "/enc/{}"           # 0..11  → int 0..127
ADDR_BTN = "/btn/{}"           # 0..7   → int 0|1
ADDR_NOTE = "/note"            # pitch, vel, track
ADDR_SEQ_STEP = "/seq/step"    # int 0..15 (tick courant)
ADDR_SEQ_TRIG = "/seq/trig/{}" # 0..3   → int 0|1 (trigger par piste)
ADDR_MODE = "/mode"            # "step" | "tracker"
ADDR_MACRO = "/macro/{}"       # 1..4   → float 0..1
ADDR_HEARTBEAT = "/heartbeat"  # ping de vie (sans argument)

# ---------------------------------------------------------------------------
# Factories de clients
# ---------------------------------------------------------------------------

def make_pd_client() -> SimpleUDPClient:
    """Retourne un client OSC UDP vers Pure Data (port 5005)."""
    return SimpleUDPClient(OSC_IP, OSC_PORT_PD)


def make_oled_client() -> SimpleUDPClient:
    """Retourne un client OSC UDP vers l'émulateur OLED (port 5006)."""
    return SimpleUDPClient(OSC_IP, OSC_PORT_OLED)
