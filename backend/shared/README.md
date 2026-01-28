# Copie du package `shared` (racine du dépôt)

Ce dossier est une **copie** de `shared/` à la racine du dépôt. Il permet au backend de trouver le module `shared` lorsque DigitalOcean App Platform utilise **Source: /backend** (seul le contenu de `backend/` est déployé).

Pour garder la copie à jour après des changements dans `shared/` :

```powershell
# Depuis la racine du dépôt (PowerShell)
Copy-Item "shared\__init__.py" "backend\shared\" -Force
Copy-Item "shared\src" "backend\shared\" -Recurse -Force
```

```bash
# Ou en bash
cp -r shared/__init__.py shared/src backend/shared/
```

Si vous utilisez **Source: /** (racine du dépôt) sur DigitalOcean, le `shared/` à la racine est utilisé et cette copie peut être ignorée.
