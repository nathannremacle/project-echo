# Architecture GitHub Actions - Project Echo

## 🎯 Vue d'Ensemble

Project Echo utilise **deux environnements différents** qui travaillent ensemble:

1. **Backend/Frontend (DigitalOcean)** → Interface de gestion et orchestration
2. **GitHub Actions (Runners GitHub)** → Traitement et publication des vidéos

## 📊 Architecture Complète

```
┌─────────────────────────────────────────────────────────────┐
│                    CENTRAL REPOSITORY                       │
│  (project-echo-orchestration)                               │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   Frontend   │────────▶│   Backend    │                │
│  │  (React)     │         │  (FastAPI)   │                │
│  │              │         │              │                │
│  └──────────────┘         └──────┬───────┘                │
│                                  │                         │
│                                  │ Orchestration           │
│                                  │                         │
└──────────────────────────────────┼─────────────────────────┘
                                   │
                                   │ Trigger via GitHub API
                                   │
┌──────────────────────────────────▼─────────────────────────┐
│              CHANNEL REPOSITORIES                           │
│  (project-echo-channel-{name})                              │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │         GitHub Actions Workflow                    │    │
│  │  (.github/workflows/process-video.yaml)           │    │
│  │                                                    │    │
│  │  1. Scrape video                                  │    │
│  │  2. Download video                                 │    │
│  │  3. Transform video                                │    │
│  │  4. Replace audio (si Phase 2)                    │    │
│  │  5. Upload to YouTube                              │    │
│  │                                                    │    │
│  │  ✅ S'exécute sur GitHub Actions (gratuit)         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  GitHub Secrets:                                            │
│  - YOUTUBE_CLIENT_ID                                        │
│  - YOUTUBE_CLIENT_SECRET                                    │
│  - YOUTUBE_REFRESH_TOKEN                                    │
│  - AWS_ACCESS_KEY_ID (pour Spaces)                          │
│  - AWS_SECRET_ACCESS_KEY                                    │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Comment Ça Fonctionne

### 1. Déploiement Backend/Frontend (DigitalOcean)

**Où:** DigitalOcean App Platform ou Droplet  
**Rôle:** Interface de gestion et orchestration

- **Frontend:** Interface web React pour gérer les chaînes
- **Backend:** API FastAPI qui:
  - Gère les chaînes et configurations
  - Orchestre les workflows GitHub Actions
  - Stocke les métadonnées dans PostgreSQL
  - Fournit l'interface de gestion

**Ce qui s'exécute ici:**
- ✅ Interface web
- ✅ API de gestion
- ✅ Base de données
- ✅ Orchestration
- ❌ **PAS** le traitement vidéo (trop lourd, utilise GitHub Actions)

### 2. Traitement Vidéo (GitHub Actions)

**Où:** GitHub Actions Runners (infrastructure GitHub)  
**Rôle:** Traitement et publication des vidéos

- **Workflow:** `.github/workflows/process-video.yaml` dans chaque channel repo
- **Exécution:** Sur les runners GitHub (ubuntu-latest)
- **Gratuit:** 2000 minutes/mois sur le plan gratuit

**Ce qui s'exécute ici:**
- ✅ Scraping de vidéos
- ✅ Download de vidéos
- ✅ Transformation (FFmpeg)
- ✅ Remplacement audio (Phase 2)
- ✅ Upload vers YouTube
- ✅ Upload vers DigitalOcean Spaces

## 🚀 Workflow Complet

### Étape 1: Configuration Initiale

1. **Déployer Backend/Frontend:**
   - Sur DigitalOcean (App Platform ou Droplet)
   - Interface accessible via URL

2. **Créer Channel Repository:**
   - Un repository GitHub par chaîne YouTube
   - Template: `templates/channel-repo-template/`

3. **Configurer GitHub Secrets:**
   - Dans chaque channel repository
   - Secrets nécessaires pour YouTube API et Spaces

### Étape 2: Workflow Automatique

```
1. Backend (DigitalOcean)
   └─▶ Détecte qu'une vidéo doit être publiée
       └─▶ Trigger GitHub Actions workflow
           └─▶ Via GitHub API (repository_dispatch)

2. GitHub Actions (Runner GitHub)
   └─▶ Workflow s'exécute:
       ├─▶ Setup Python + FFmpeg
       ├─▶ Install dependencies
       ├─▶ Scrape video
       ├─▶ Download video
       ├─▶ Transform video
       ├─▶ Replace audio (si Phase 2)
       ├─▶ Upload to YouTube
       └─▶ Upload to Spaces (backup)

3. Backend (DigitalOcean)
   └─▶ Met à jour les métadonnées
       └─▶ Affiche dans l'interface
```

## ⚙️ Configuration GitHub Actions

### Workflow Template

Chaque channel repository a un workflow:

```yaml
# .github/workflows/process-video.yaml
name: Process and Publish Video

on:
  # Manuel depuis l'interface GitHub
  workflow_dispatch:
    inputs:
      video_url:
        description: 'URL of video to process'
        required: false
  
  # Automatique selon planning
  schedule:
    - cron: '0 */6 * * *'  # Toutes les 6 heures
  
  # Déclenché par le backend central
  repository_dispatch:
    types: [process-video]

jobs:
  process-video:
    runs-on: ubuntu-latest
    timeout-minutes: 360  # 6h max (limite GitHub Actions)
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install FFmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
      
      - name: Install dependencies
        run: |
          pip install git+https://github.com/user/project-echo-orchestration.git#subdirectory=shared
          pip install -r requirements.txt
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: nyc3
          endpoint-url: https://nyc3.digitaloceanspaces.com
      
      - name: Process and publish video
        env:
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
        run: |
          python scripts/process_video.py
```

### Secrets Nécessaires (Par Channel Repository)

Dans chaque channel repository, configurez ces secrets:

1. **YouTube API:**
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

2. **DigitalOcean Spaces (S3-compatible):**
   - `AWS_ACCESS_KEY_ID` (Access Key Spaces)
   - `AWS_SECRET_ACCESS_KEY` (Secret Key Spaces)

3. **Optionnel:**
   - `CHANNEL_ID` (UUID de la chaîne depuis le backend)

## 💰 Coûts

### Backend/Frontend (DigitalOcean)
- **App Platform:** $25/mois
- **Droplet:** $11/mois
- **Gratuit** avec vos $200 de crédits

### GitHub Actions
- **Gratuit:** 2000 minutes/mois
- **Calcul:**
  - 1 vidéo = ~10-30 minutes de traitement
  - 2000 minutes = ~66-200 vidéos/mois
  - **Suffisant pour démarrer!**

### Si vous dépassez 2000 min/mois:
- **Option 1:** Passer au plan GitHub Pro ($4/mois) = 3000 min/mois
- **Option 2:** Utiliser un Droplet pour le traitement vidéo
- **Option 3:** Optimiser les workflows (parallélisation)

## 🔧 Pourquoi Cette Architecture?

### Avantages

1. **Gratuit:** GitHub Actions gratuit jusqu'à 2000 min/mois
2. **Scalable:** Chaque channel a son propre workflow
3. **Isolé:** Un problème dans un channel n'affecte pas les autres
4. **Flexible:** Peut déclencher manuellement ou automatiquement
5. **Monitoring:** GitHub Actions fournit des logs détaillés

### Limitations GitHub Actions

1. **Timeout:** 6 heures max par workflow
2. **Ressources:** Limitée (2 CPU, 7GB RAM)
3. **Quota:** 2000 min/mois gratuit

**Solution:** Pour des vidéos très longues ou beaucoup de vidéos, on peut migrer vers un Droplet dédié au traitement.

## 📝 Checklist de Configuration

### Backend/Frontend (DigitalOcean)
- [ ] Déployé sur DigitalOcean
- [ ] PostgreSQL configuré
- [ ] DigitalOcean Spaces configuré
- [ ] Variables d'environnement configurées
- [ ] Interface accessible

### Channel Repository (GitHub)
- [ ] Repository créé pour chaque channel
- [ ] Workflow `.github/workflows/process-video.yaml` copié
- [ ] GitHub Secrets configurés:
  - [ ] YOUTUBE_CLIENT_ID
  - [ ] YOUTUBE_CLIENT_SECRET
  - [ ] YOUTUBE_REFRESH_TOKEN
  - [ ] AWS_ACCESS_KEY_ID
  - [ ] AWS_SECRET_ACCESS_KEY
- [ ] Workflow testé manuellement

### Intégration
- [ ] Backend peut déclencher workflows (GitHub API)
- [ ] Workflows peuvent accéder à Spaces
- [ ] Workflows peuvent publier sur YouTube
- [ ] Métadonnées synchronisées avec backend

## 🚨 Points Importants

1. **Deux Environnements:**
   - Backend/Frontend = DigitalOcean (toujours actif)
   - Traitement vidéo = GitHub Actions (s'exécute à la demande)

2. **GitHub Actions est Gratuit:**
   - 2000 minutes/mois = suffisant pour démarrer
   - Chaque vidéo = ~10-30 minutes
   - = ~66-200 vidéos/mois

3. **Workflows Sont Déclenchés:**
   - Automatiquement (schedule/cron)
   - Manuellement (depuis GitHub UI)
   - Par le backend (via GitHub API)

4. **Chaque Channel = Un Repository:**
   - Isolation complète
   - Secrets séparés
   - Workflows indépendants

## 📚 Documentation Complète

- **Setup GitHub Actions:** [docs/GITHUB-ACTIONS-SETUP.md](GITHUB-ACTIONS-SETUP.md)
- **Multi-Repo Architecture:** [docs/MULTI-REPO-ARCHITECTURE.md](MULTI-REPO-ARCHITECTURE.md)
- **Déploiement:** [docs/DEPLOYMENT.md](DEPLOYMENT.md)

## ✅ Résumé

**Oui, les scripts passent sur GitHub Actions!**

- Le backend/frontend est déployé sur DigitalOcean
- Le traitement vidéo s'exécute sur GitHub Actions (gratuit)
- Les deux communiquent via GitHub API
- Chaque channel a son propre workflow GitHub Actions

**C'est gratuit et scalable! 🚀**
