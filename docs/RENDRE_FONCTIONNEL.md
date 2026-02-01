# Checklist : Rendre Project Echo fonctionnel sur DigitalOcean

Ce guide liste les étapes pour que le pipeline (ajouter vidéo → scrape → download → transform → publish) fonctionne de bout en bout sur **DigitalOcean + GitHub**.

---

## Prérequis

- [ ] Compte GitHub
- [ ] Compte DigitalOcean (crédits $200)
- [ ] Compte Google Cloud (pour YouTube API)

---

## 1. DigitalOcean Spaces (stockage vidéos)

Le pipeline a besoin de stocker les vidéos téléchargées et transformées. **DigitalOcean Spaces** est l’équivalent S3 de DigitalOcean.

1. [ ] Aller sur [DigitalOcean Spaces](https://cloud.digitalocean.com/spaces)
2. [ ] Créer un Space (ex. `project-echo-videos`)
3. [ ] Récupérer :
   - **Access Key** (Spaces Keys)
   - **Secret Key**
   - **Bucket name**
   - **Endpoint** (ex. `nyc3.digitaloceanspaces.com`)

---

## 2. Déploiement sur App Platform

1. [ ] Pousser le code sur GitHub
2. [ ] Créer une App sur [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
3. [ ] Connecter le dépôt GitHub
4. [ ] Configurer le **backend** (Source = `/backend` ou repo root selon votre Procfile)
5. [ ] Ajouter une base **PostgreSQL**
6. [ ] Configurer le **frontend** (Source = `/frontend`)

---

## 3. Variables d’environnement (backend)

À configurer dans App Platform → Backend → Settings → App-Level Environment Variables :

| Variable | Valeur | Obligatoire |
|----------|--------|-------------|
| `DATABASE_URL` | Auto-généré par la DB | Oui |
| `AWS_ACCESS_KEY_ID` | Access Key Spaces | Oui |
| `AWS_SECRET_ACCESS_KEY` | Secret Key Spaces | Oui |
| `AWS_S3_BUCKET` | Nom du Space | Oui |
| `AWS_REGION` | `nyc3` (ou votre région) | Oui |
| `S3_ENDPOINT_URL` | `nyc3.digitaloceanspaces.com` | Oui |
| `ENCRYPTION_KEY` | 32 caractères aléatoires | Oui |
| `CORS_ORIGINS` | URL du frontend (ex. `https://xxx.ondigitalocean.app`) | Oui |
| `APP_ENV` | `production` | Recommandé |

---

## 4. Migrations et seed

- **Migrations** : exécutées automatiquement au démarrage du backend (`start.sh`).
- **Seed** : après le premier déploiement, exécuter `python scripts/seed_db.py` pour créer la chaîne de test et les configs par défaut. Sur App Platform : via un **job** ou la console (Run Command).

---

## 5. Configuration YouTube OAuth

1. [ ] Créer un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. [ ] Activer **YouTube Data API v3**
3. [ ] Créer des credentials **OAuth 2.0** (Desktop app)
4. [ ] Obtenir un **Refresh Token** via `python scripts/setup_youtube_oauth.py credentials.json`
5. [ ] Dans l’interface Project Echo : **Channels** → votre chaîne → **Credentials YouTube OAuth** → remplir Client ID, Client Secret, Refresh Token

---

## 6. Preset de transformation (optionnel)

- [ ] **Settings** → **Transformation Presets** → créer un preset (ex. "moderate")
- [ ] Associer le preset à la chaîne dans sa configuration (`effect_preset_id`)

Si aucun preset n’est associé, le système utilise le preset par défaut "moderate".

---

## 7. Tester le pipeline

1. [ ] Créer une chaîne (ou utiliser la chaîne de test)
2. [ ] Configurer OAuth YouTube sur la chaîne
3. [ ] **Queue** → **Ajouter une vidéo** → coller une URL YouTube publique
4. [ ] Vérifier que la vidéo passe par : scrape → download → transform → publish

---

## Erreurs fréquentes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `S3/Spaces credentials required in production` | Variables Spaces non configurées | Configurer `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc. |
| `Pipeline failed at download` | Spaces mal configuré ou endpoint incorrect | Vérifier `S3_ENDPOINT_URL` (ex. `nyc3.digitaloceanspaces.com`) |
| `Pipeline failed at transform` | FFmpeg manquant ou preset invalide | Vérifier que FFmpeg est installé (buildpack ou image) |
| `Pipeline failed at upload` | OAuth YouTube non configuré | Configurer les credentials sur la chaîne |
| Timeout après ~6 secondes | Timeout frontend ou load balancer | Timeout frontend = 5 min. Vérifier timeout App Platform si besoin. |

---

## Références

- [QUICK_START.md](./QUICK_START.md) — Déploiement détaillé
- [CONFIGURATION_DIGITALOCEAN.md](./CONFIGURATION_DIGITALOCEAN.md) — Config Spaces
- [COMMENT_CA_MARCHE.md](./COMMENT_CA_MARCHE.md) — Vue d’ensemble
