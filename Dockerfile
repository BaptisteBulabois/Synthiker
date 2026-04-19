# Dockerfile — Synthiker backend (Python)
# Contient : sequencer.py, ai_gen.py, tracker_mode.py
# Pure Data et fake_panel.py restent sur l'hôte Windows.

FROM python:3.11-slim

# Dépendances OS minimales (aucune dépendance audio/graphique nécessaire ici)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les dépendances en premier pour profiter du cache Docker
COPY requirements.txt .

# Installer uniquement les dépendances nécessaires au backend (pas de pygame/luma)
RUN pip install --no-cache-dir \
        python-osc \
        numpy \
        mido \
        python-rtmidi

# Copier le reste du projet
COPY . .

# Variable d'environnement par défaut — surchargée par docker-compose.yml
ENV PD_HOST=127.0.0.1

# Lancer le superviseur backend
CMD ["python", "-u", "sim/backend_supervisor.py"]
