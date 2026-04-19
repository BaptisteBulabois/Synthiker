"""
backend_supervisor.py — Superviseur de la stack backend Synthiker.

Lance les scripts Python du backend (sequencer, ai_gen, tracker_mode)
en sous-processus et gère l'arrêt propre sur SIGINT/SIGTERM.

Variables d'environnement :
    ENABLE_TRACKER=1   Active tracker_mode.py (désactivé par défaut)
    PD_HOST            Hôte Pure Data pour OSC (hérité par les sous-processus)

Usage :
    python sim/backend_supervisor.py
"""

import collections
import os
import signal
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# Paramètres de redémarrage
# ---------------------------------------------------------------------------
# Nombre maximum de redémarrages dans RESTART_WINDOW secondes avant abandon.
MAX_RESTARTS = 5
RESTART_WINDOW = 30.0   # secondes
RESTART_DELAY = 2.0     # secondes d'attente avant chaque redémarrage

# ---------------------------------------------------------------------------
# Processus à lancer
# ---------------------------------------------------------------------------
SCRIPTS = [
    [sys.executable, "-u", "sim/sequencer.py"],
    [sys.executable, "-u", "sim/ai_gen.py"],
]

if os.environ.get("ENABLE_TRACKER", "0") == "1":
    SCRIPTS.append([sys.executable, "-u", "sim/tracker_mode.py"])


# ---------------------------------------------------------------------------
# Gestion d'un processus enfant avec compteur de redémarrages
# ---------------------------------------------------------------------------

class _Child:
    """Encapsule un processus enfant avec logique de redémarrage bornée."""

    def __init__(self, cmd: list) -> None:
        self.cmd = cmd
        self.proc: subprocess.Popen = None
        self._restart_times: collections.deque = collections.deque()
        self.gave_up: bool = False
        self._reported_dead: bool = False

    def start(self) -> None:
        label = " ".join(self.cmd)
        print(f"[supervisor] Démarrage : {label}", flush=True)
        self.proc = subprocess.Popen(
            self.cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        self._reported_dead = False

    def poll(self):
        return None if self.proc is None else self.proc.poll()

    def handle_exit(self, ret: int) -> None:
        """Appelé une seule fois quand le processus vient de se terminer."""
        label = " ".join(self.cmd)
        print(
            f"[supervisor] ⚠️  Processus {label!r} terminé avec code {ret}",
            flush=True,
        )
        print(
            "[supervisor] 💡 Pour voir la cause : "
            "docker compose logs --tail=200 backend",
            flush=True,
        )

    def should_restart(self) -> bool:
        if self.gave_up:
            return False
        now = time.monotonic()
        while self._restart_times and now - self._restart_times[0] > RESTART_WINDOW:
            self._restart_times.popleft()
        if len(self._restart_times) >= MAX_RESTARTS:
            self.gave_up = True
            label = " ".join(self.cmd)
            print(
                f"[supervisor] ❌ {label!r} a dépassé {MAX_RESTARTS} redémarrages "
                f"en {RESTART_WINDOW:.0f}s — abandon.",
                flush=True,
            )
            return False
        return True

    def restart(self) -> None:
        self._restart_times.append(time.monotonic())
        n = len(self._restart_times)
        label = " ".join(self.cmd)
        print(
            f"[supervisor] 🔄 Redémarrage #{n} de {label!r} "
            f"dans {RESTART_DELAY:.0f}s...",
            flush=True,
        )
        time.sleep(RESTART_DELAY)
        self.start()


# ---------------------------------------------------------------------------
# Démarrage et arrêt
# ---------------------------------------------------------------------------

def start_children() -> list:
    children = []
    for cmd in SCRIPTS:
        child = _Child(cmd)
        child.start()
        children.append(child)
    return children


def shutdown(children: list, timeout: float = 5.0) -> None:
    print("[supervisor] Arrêt en cours...", flush=True)
    for child in children:
        if child.poll() is None and child.proc is not None:
            child.proc.terminate()

    deadline = time.monotonic() + timeout
    for child in children:
        if child.proc is None:
            continue
        remaining = max(0.0, deadline - time.monotonic())
        try:
            child.proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            print(f"[supervisor] Forçage arrêt PID {child.proc.pid}", flush=True)
            child.proc.kill()

    print("[supervisor] Tous les processus arrêtés.", flush=True)


def main() -> None:
    children = start_children()

    def _handler(signum, _frame):
        try:
            shutdown(children)
        finally:
            sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)

    print("[supervisor] Stack backend démarrée. Ctrl+C pour arrêter.", flush=True)

    # Surveille les enfants, relève les sorties anormales et redémarre si besoin
    while True:
        time.sleep(1)
        for child in children:
            ret = child.poll()
            if ret is not None and not child._reported_dead:
                child._reported_dead = True
                child.handle_exit(ret)
                if ret != 0 and child.should_restart():
                    child.restart()

        # Si tous les enfants ont abandonné ou sont morts sans redémarrage, on sort
        all_done = all(
            child.gave_up or (child.poll() is not None and child._reported_dead)
            for child in children
        )
        if all_done:
            print("[supervisor] Tous les processus fils terminés, sortie.", flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
