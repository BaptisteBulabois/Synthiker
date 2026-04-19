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

import os
import signal
import subprocess
import sys
import time

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
# Démarrage des sous-processus
# ---------------------------------------------------------------------------

def start_children() -> list[subprocess.Popen]:
    children = []
    for cmd in SCRIPTS:
        print(f"[supervisor] Démarrage : {' '.join(cmd)}", flush=True)
        proc = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        children.append(proc)
    return children


def shutdown(children: list[subprocess.Popen], timeout: float = 5.0) -> None:
    print("[supervisor] Arrêt en cours...", flush=True)
    for proc in children:
        if proc.poll() is None:
            proc.terminate()

    deadline = time.monotonic() + timeout
    for proc in children:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            print(f"[supervisor] Forçage arrêt PID {proc.pid}", flush=True)
            proc.kill()

    print("[supervisor] Tous les processus arrêtés.", flush=True)


def main() -> None:
    children = start_children()

    def _handler(signum, _frame):
        shutdown(children)
        sys.exit(0)

    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)

    print("[supervisor] Stack backend démarrée. Ctrl+C pour arrêter.", flush=True)

    # Surveille les enfants et relève les retours anormaux
    while True:
        time.sleep(1)
        for proc in children:
            ret = proc.poll()
            if ret is not None:
                print(
                    f"[supervisor] ⚠️  Processus {proc.args} terminé avec code {ret}",
                    flush=True,
                )
        # Si tous les enfants sont morts, on sort
        if all(proc.poll() is not None for proc in children):
            print("[supervisor] Tous les processus fils terminés, sortie.", flush=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
