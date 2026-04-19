# Guide Docker — Synthiker (Windows, approche hybride)

Ce guide explique comment faire tourner la **stack backend** de Synthiker dans un container Docker sur Windows, tout en gardant **Pure Data** (audio) et **fake_panel** (UI PyGame) sur la machine hôte.

---

## Architecture hybride

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│  Hôte Windows               │  OSC    │  Container Docker           │
│                             │ :5005   │                             │
│  • Pure Data synth_main.pd  │◄────────│  • sequencer.py             │
│  • fake_panel.py (PyGame)   │         │  • ai_gen.py                │
│                             │         │  • tracker_mode.py (opt.)   │
└─────────────────────────────┘         └─────────────────────────────┘
```

Les scripts backend envoient des messages OSC vers Pure Data via `host.docker.internal:5005` — une adresse DNS spéciale que Docker Desktop résout automatiquement vers votre machine Windows.

---

## Prérequis

### 1. Docker Desktop pour Windows

1. Téléchargez **Docker Desktop** : <https://www.docker.com/products/docker-desktop/>
2. Installez avec l'option **"Use WSL 2 instead of Hyper-V"** cochée.
3. Redémarrez votre PC si demandé.
4. Lancez **Docker Desktop** depuis le menu Démarrer.

Vérification dans PowerShell :

```powershell
docker --version
docker compose version
docker run hello-world
```

Vous devez voir `Hello from Docker!` ✅

### 2. Python 3.11+ sur l'hôte

Nécessaire pour `fake_panel.py` uniquement. Voir le [guide de simulation](simulation_guide.md) pour l'installation du venv.

### 3. Pure Data vanilla ≥ 0.54

Téléchargement : <https://puredata.info/downloads>

---

## Étape 1 — Lancer Pure Data sur l'hôte

1. Ouvrez Pure Data (depuis le menu Démarrer ou en ligne de commande) :

   ```powershell
   pd pd_patches\synth_main.pd
   ```

2. Dans Pure Data, **activez le DSP** :
   - Menu **Media → DSP On** ou cochez la case **DSP** en haut à droite.
   - Vous devez voir la case cochée et entendre un léger "clic" de démarrage.

> ⚠️ Sans DSP activé, vous n'entendrez aucun son même si les OSC arrivent correctement.

---

## Étape 2 — Lancer fake_panel sur l'hôte (optionnel)

Dans un terminal PowerShell séparé :

```powershell
# Activer le venv
.\venv\Scripts\Activate.ps1

# Lancer l'interface
python sim\fake_panel.py
```

Une fenêtre PyGame apparaît avec 12 encodeurs et 8 boutons.

---

## Étape 3 — Démarrer le container backend

Dans un terminal PowerShell à la racine du repo :

```powershell
docker compose up --build
```

Ce que vous devez voir :

```
[+] Building ...
...
backend-1  | [supervisor] Démarrage : python -u sim/sequencer.py
backend-1  | [supervisor] Démarrage : python -u sim/ai_gen.py
backend-1  | [supervisor] Stack backend démarrée. Ctrl+C pour arrêter.
backend-1  | [sequencer] Tick 0 — kick=1 snare=0 hat=0 clap=0
backend-1  | [ai_gen] Génération pattern Markov...
...
```

### Activer le mode tracker (optionnel)

```powershell
$env:ENABLE_TRACKER="1"; docker compose up --build
```

---

## Étape 4 — Arrêter le container

Appuyez sur **Ctrl+C** dans le terminal où tourne `docker compose up`.

Le superviseur envoie SIGTERM à tous les sous-processus et attend leur arrêt propre.

Pour forcer l'arrêt complet :

```powershell
docker compose down
```

---

## Dépannage

### ❌ Pure Data ne reçoit pas les OSC

**Symptôme** : Les logs Docker montrent des messages mais aucun son.

**Causes fréquentes** :

1. **DSP non activé** dans Pure Data → Media → DSP On.
2. **Pare-feu Windows** bloque le port UDP 5005.
   - Menu Démarrer → "Autoriser une application via le Pare-feu Windows".
   - Cliquez "Modifier les paramètres" → "Autoriser une autre application".
   - Cherchez `pd.exe` et autorisez les réseaux privés ET publics.
   - Ou via PowerShell (admin) :
     ```powershell
     New-NetFirewallRule -DisplayName "Pure Data OSC" -Direction Inbound -Protocol UDP -LocalPort 5005 -Action Allow
     ```
3. **`host.docker.internal` non résolu** → rare avec Docker Desktop récent.
   Vérifiez avec :
   ```powershell
   docker run --rm alpine nslookup host.docker.internal
   ```
   Vous devez voir une adresse IP de type `192.168.x.x`.

### ❌ Erreur `port is already allocated`

Un autre processus utilise déjà le port. Vérifiez :

```powershell
netstat -ano | findstr :5005
```

Terminez le processus concerné ou changez le port dans Pure Data et dans `sim/osc_bridge.py`.

### ❌ Erreur de build Docker : `gcc` introuvable

L'image `python:3.11-slim` inclut `gcc` via le Dockerfile. Si vous obtenez une erreur réseau lors du build, vérifiez votre connexion et réessayez :

```powershell
docker compose build --no-cache
```

### ✅ Vérifier que les paquets UDP arrivent dans Pure Data

Dans le patch `synth_main.pd`, le message de debug OSC peut être affiché avec un objet `print`. Vous pouvez aussi utiliser **Wireshark** et filtrer sur `udp.port == 5005` pour confirmer les paquets.

---

## Références

- [Guide de simulation complet](simulation_guide.md)
- [Protocole OSC](osc_protocol.md)
- [Docker Desktop pour Windows](https://docs.docker.com/desktop/install/windows-install/)
- [WSL 2 — documentation Microsoft](https://docs.microsoft.com/fr-fr/windows/wsl/install)
