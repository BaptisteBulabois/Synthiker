"""
ai_gen.py — Génération de patterns drums via chaîne de Markov (ordre 1).

Fallback Markov. Version Magenta (réseau neuronal RNN) en PR #3.

Principe :
  - Un dataset de patterns kick amorcent la chaîne.
  - La matrice de transition est calculée depuis ces patterns.
  - Toutes les 8 secondes un nouveau pattern 16 pas est généré et envoyé
    via OSC vers Pure Data (/seq/kick/0..15).

Usage :
    python sim/ai_gen.py
"""

import sys
import time
import random

import numpy as np

sys.path.insert(0, __file__.replace("/sim/ai_gen.py", ""))

from sim.osc_bridge import make_pd_client

# ---------------------------------------------------------------------------
# Dataset d'amorçage (patterns kick 16 pas)
# ---------------------------------------------------------------------------
SEED_PATTERNS = [
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # four-on-the-floor
    [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # variation 1
    [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1],  # variation 2
    [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],  # sparse
    [1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0],  # dense
]

# ---------------------------------------------------------------------------
# Construction de la matrice de transition Markov (ordre 1)
# ---------------------------------------------------------------------------

def build_transition_matrix(patterns: list[list[int]]) -> np.ndarray:
    """Construit une matrice de transition 2×2 depuis les patterns.

    État 0 = pas de kick, état 1 = kick.
    transition[i][j] = probabilité de passer de l'état i à l'état j.
    """
    counts = np.ones((2, 2))  # initialisation Laplace (évite les proba 0)
    for pattern in patterns:
        for a, b in zip(pattern[:-1], pattern[1:]):
            counts[a][b] += 1
    # Normalisation par ligne
    return counts / counts.sum(axis=1, keepdims=True)


TRANSITION = build_transition_matrix(SEED_PATTERNS)


def generate_pattern(length: int = 16, start: int = 1) -> list[int]:
    """Génère un pattern de longueur `length` via la chaîne de Markov."""
    pattern = [start]
    for _ in range(length - 1):
        state = pattern[-1]
        # Tirage selon les probabilités de transition
        next_state = int(np.random.choice([0, 1], p=TRANSITION[state]))
        pattern.append(next_state)
    return pattern


def visualize(pattern: list[int]) -> str:
    """Retourne une représentation visuelle ASCII du pattern."""
    return "".join("█" if s else "_" for s in pattern)


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

def run_ai_gen(interval: float = 8.0) -> None:
    """Génère et envoie un nouveau pattern toutes les `interval` secondes."""
    client = make_pd_client()
    print(f"[AI] Démarrage — génération toutes les {interval}s")
    print("[AI] Ctrl+C pour arrêter\n")

    # Kick de départ aléatoire parmi le dataset
    start_state = random.choice(SEED_PATTERNS)[0]

    try:
        iteration = 0
        while True:
            pattern = generate_pattern(16, start_state)
            viz = visualize(pattern)
            print(f"[AI] Iter {iteration:04d} | {viz}")

            # Envoi OSC
            for i, val in enumerate(pattern):
                client.send_message(f"/seq/kick/{i}", val)

            # Le prochain départ = dernier état du pattern
            start_state = pattern[-1]
            iteration += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[AI] Arrêt propre.")


def main() -> None:
    """Point d'entrée."""
    run_ai_gen(interval=8.0)


if __name__ == "__main__":
    main()
