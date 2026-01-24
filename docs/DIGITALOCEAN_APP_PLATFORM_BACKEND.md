# DigitalOcean App Platform – Backend (shared module)

## Fix for `ModuleNotFoundError: No module named 'shared'`

The backend imports the **`shared`** package (scraping, download, transformation) from the repository root:

```
from shared.src.scraping import YouTubeScraper, ...
from shared.src.download import S3StorageClient, ...
from shared.src.transformation import VideoTransformer, ...
```

If the backend component uses **Source: `/backend`**, only the `backend/` directory is deployed and `shared/` is missing → `ModuleNotFoundError: No module named 'shared'`.

## Solution: Use the repository root as source

1. **Source / Root directory**  
   Set the backend component’s **Source** to the **repository root** (`/` or blank), **not** `/backend`.  
   The repo root must contain both `backend/` and `shared/`.

2. **Build command**
   ```bash
   cd backend && pip install -r requirements.txt
   ```

3. **Run command**
   - Either rely on the **root `Procfile`** (`web: sh backend/start.sh`), or  
   - Set **Run command** explicitly to:
     ```bash
     sh backend/start.sh
     ```

`backend/start.sh` adds the repo root to `PYTHONPATH` so `shared` can be imported.

## Summary

| Setting        | Incorrect (causes error) | Correct                          |
|----------------|---------------------------|----------------------------------|
| Source         | `/backend`                | `/` or repository root           |
| Build command  | `pip install -r requirements.txt` | `cd backend && pip install -r requirements.txt` |
| Run command    | `uvicorn src.main:app …`  | `sh backend/start.sh` (or use root Procfile) |

## App spec (YAML)

If you use an app spec (e.g. `app.yaml` or `.do/app.yaml`), for the backend service use:

```yaml
services:
  - name: api
    source_dir: /
    build_command: cd backend && pip install -r requirements.txt
    run_command: sh backend/start.sh
    environment_slug: python
    http_port: 8080
    # github, envs, etc.
```

`source_dir: /` (or omitting it so it defaults to the repo root) ensures both `backend/` and `shared/` are in the build and at runtime.
