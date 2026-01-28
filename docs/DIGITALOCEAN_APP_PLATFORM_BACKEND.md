# DigitalOcean App Platform – Backend (module shared)

## Correction de `ModuleNotFoundError: No module named 'shared'`

Le backend importe le package **`shared`** (scraping, download, transformation) :

```
from shared.src.scraping import YouTubeScraper, ...
from shared.src.download import S3StorageClient, ...
from shared.src.transformation import VideoTransformer, ...
```

### Solution recommandée : Installer le package `shared`

Le package `shared` peut maintenant être installé comme un package Python normal :

**Option 1 : Installation depuis la racine (recommandé si Source = `/`)**
```bash
# Dans la commande Build
cd backend && pip install -r requirements.txt && pip install -e ../shared
```

**Option 2 : Utiliser `backend/shared` (copie intégrée)**
Une **copie** du package `shared` se trouve dans `backend/shared/`. Avec **Source : `/backend`**, ce dossier est inclus dans le déploiement.

Une **copie** du package `shared` se trouve dans `backend/shared/`. Avec **Source : `/backend`**, ce dossier est inclus dans le déploiement.

- **Run** : utilisez `sh start.sh` (Procfile par défaut : `web: sh start.sh`) pour que `start.sh` mette le répertoire de travail dans `PYTHONPATH` et que `shared` soit trouvé.
- Si la **Run command** est `uvicorn src.main:app --host 0.0.0.0 --port $PORT`, le répertoire courant est en général déjà dans `sys.path`, donc `backend/shared` peut suffire. En cas d’erreur, utilisez `sh start.sh`.

### Option : utiliser la racine du dépôt (Source : `/`)

1. **Source** : `/` (racine du dépôt).
2. **Build** : `cd backend && pip install -r requirements.txt`
3. **Run** : `sh backend/start.sh`

Dans ce cas, c’est le `shared/` à la racine qui est utilisé.

## Résumé (Source = `/backend`)

| Paramètre | Valeur |
|-----------|--------|
| Source | `/backend` (OK : `backend/shared` est inclus) |
| Build | `pip install -r requirements.txt` (le `backend/shared` est utilisé via PYTHONPATH) |
| Run | `sh start.sh` (Procfile par défaut) ou `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |

## Résumé (Source = `/` - Recommandé)

| Paramètre | Valeur |
|-----------|--------|
| Source | `/` (racine du dépôt) |
| Build | `cd backend && pip install -r requirements.txt && pip install -e ../shared` |
| Run | `sh backend/start.sh` |

## Garder `backend/shared` à jour

Après modification de `shared/` à la racine, resynchroniser :

```powershell
# PowerShell (depuis la racine du dépôt)
Copy-Item "shared\__init__.py" "backend\shared\" -Force
Copy-Item "shared\src" "backend\shared\" -Recurse -Force
```

Voir aussi `backend/shared/README.md`.
