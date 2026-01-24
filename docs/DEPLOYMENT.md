# Guide de Déploiement et Utilisation - Project Echo

## Vue d'ensemble

Ce guide vous explique comment déployer et utiliser Project Echo pour automatiser la création, transformation et publication de vidéos sur plusieurs chaînes YouTube.

**⚠️ Important:** Project Echo utilise **deux environnements**:
1. **Backend/Frontend** → Déployé sur DigitalOcean (interface de gestion)
2. **GitHub Actions** → Traitement vidéo (gratuit, 2000 min/mois)

Voir [ARCHITECTURE_GITHUB_ACTIONS.md](ARCHITECTURE_GITHUB_ACTIONS.md) pour comprendre comment tout fonctionne ensemble.

## Architecture de Déploiement Recommandée (Gratuit avec DigitalOcean)

### Option 1: DigitalOcean App Platform (Recommandé - Gratuit avec crédits)

**Coûts estimés:**
- **App Platform Basic**: $5/mois (gratuit avec vos crédits pendant 1 an)
- **Managed PostgreSQL**: $15/mois (gratuit avec crédits)
- **Spaces (S3-compatible)**: $5/mois (gratuit avec crédits)
- **Total**: ~$25/mois = **GRATUIT pendant 1 an avec vos $200**

**Avantages:**
- Déploiement automatique depuis GitHub
- Scaling automatique
- HTTPS inclus
- Base de données gérée
- Storage S3-compatible

### Option 2: Droplet DigitalOcean (Plus économique)

**Coûts estimés:**
- **Droplet Basic ($6/mois)**: Backend + Frontend + PostgreSQL
- **Spaces ($5/mois)**: Stockage vidéos
- **Total**: ~$11/mois = **GRATUIT pendant ~18 mois avec vos $200**

**Avantages:**
- Plus économique
- Contrôle total
- Peut héberger tout sur un seul serveur

## Prérequis

### 1. Comptes Nécessaires

- **GitHub**: Pour le code et GitHub Actions (gratuit)
- **DigitalOcean**: Pour l'hébergement (vous avez $200 de crédits)
- **YouTube Data API**: Pour publier des vidéos (gratuit)
- **AWS S3 ou DigitalOcean Spaces**: Pour stocker les vidéos (Spaces recommandé - $5/mois)

### 2. Outils Locaux

- Python 3.11+
- Node.js 18+
- Git
- FFmpeg (pour le traitement vidéo local si test)

## Configuration Initiale

### Étape 1: Configuration YouTube API

1. **Créer un projet Google Cloud:**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un nouveau projet
   - Activez l'API "YouTube Data API v3"

2. **Créer des credentials OAuth 2.0:**
   - Allez dans "APIs & Services" > "Credentials"
   - Créez des "OAuth 2.0 Client ID"
   - Type: "Desktop app"
   - Téléchargez le fichier JSON

3. **Obtenir un refresh token:**
   - Utilisez le script `backend/scripts/setup_youtube_oauth.py` (à créer)
   - Ou suivez le guide OAuth 2.0 de Google
   - Vous aurez besoin d'un `client_id`, `client_secret`, et `refresh_token` pour chaque chaîne

### Étape 2: Configuration DigitalOcean Spaces (S3-compatible)

1. **Créer un Space:**
   - Allez sur DigitalOcean > Spaces
   - Créez un nouveau Space
   - Région: Choisissez la plus proche
   - Notez: `Endpoint`, `Access Key`, `Secret Key`

2. **Configuration CORS:**
   - Activez CORS pour permettre les uploads depuis votre backend
   - Configuration recommandée:
   ```json
   {
     "AllowedOrigins": ["*"],
     "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
     "AllowedHeaders": ["*"]
   }
   ```

### Étape 3: Configuration GitHub Secrets

Pour chaque repository (central + channel repos), configurez:

**Secrets nécessaires:**
- `YOUTUBE_CLIENT_ID`: Client ID OAuth 2.0
- `YOUTUBE_CLIENT_SECRET`: Client Secret OAuth 2.0
- `YOUTUBE_REFRESH_TOKEN`: Refresh token (par chaîne)
- `S3_ACCESS_KEY`: Access key DigitalOcean Spaces
- `S3_SECRET_KEY`: Secret key DigitalOcean Spaces
- `S3_BUCKET_NAME`: Nom du Space
- `S3_ENDPOINT_URL`: Endpoint du Space (ex: `nyc3.digitaloceanspaces.com`)
- `DATABASE_URL`: URL de connexion PostgreSQL (si utilisé)

## Déploiement sur DigitalOcean

### Option A: App Platform (Recommandé)

#### 1. Préparer le Repository

```bash
# Assurez-vous que votre code est sur GitHub
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Créer l'Application sur DigitalOcean

1. **Connecter GitHub:**
   - Allez sur DigitalOcean > App Platform
   - Cliquez "Create App"
   - Connectez votre compte GitHub
   - Sélectionnez le repository

2. **Configurer le Backend:**
   - **Type**: Web Service
   - **Source**: `/` (racine du dépôt, **pas** `/backend`) — nécessaire pour que le module `shared` (sibling de `backend/`) soit disponible. Voir [DIGITALOCEAN_APP_PLATFORM_BACKEND.md](DIGITALOCEAN_APP_PLATFORM_BACKEND.md).
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Run Command**: 
     ```bash
     sh backend/start.sh
     ```
     (ou laisser le Procfile à la racine : `web: sh backend/start.sh`)
   - **Environment Variables**:
     ```
     DATABASE_URL=<postgresql-url>
     S3_ACCESS_KEY=<your-key>
     S3_SECRET_KEY=<your-secret>
     S3_BUCKET_NAME=<your-bucket>
     S3_ENDPOINT_URL=<your-endpoint>
     ENCRYPTION_KEY=<random-32-char-key>
     CORS_ORIGINS=https://your-frontend-url.com
     ```

3. **Ajouter PostgreSQL Database:**
   - Dans App Platform, ajoutez une "Database" component
   - Type: PostgreSQL
   - Version: 14 ou 15
   - La variable `DATABASE_URL` sera automatiquement injectée

4. **Configurer le Frontend:**
   - **Type**: Static Site
   - **Source**: `/frontend`
   - **Build Command**: 
     ```bash
     npm install && npm run build
     ```
   - **Output Directory**: `dist`
   - **Environment Variables**:
     ```
     VITE_API_BASE_URL=https://your-backend-url.com
     ```

#### 3. Déployer

- DigitalOcean déploiera automatiquement à chaque push sur `main`
- Les URLs seront générées automatiquement
- HTTPS est inclus automatiquement

### Option B: Droplet (Plus économique)

#### 1. Créer un Droplet

```bash
# Sur DigitalOcean, créez un Droplet:
# - Image: Ubuntu 22.04
# - Plan: Basic $6/mois (1GB RAM, 1 vCPU)
# - Region: Choisissez la plus proche
# - Authentication: SSH keys (recommandé)
```

#### 2. Configuration Initiale du Serveur

```bash
# Connectez-vous au serveur
ssh root@your-droplet-ip

# Mettre à jour le système
apt update && apt upgrade -y

# Installer les dépendances
apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql ffmpeg git

# Installer pnpm
npm install -g pnpm

# Créer un utilisateur pour l'application
adduser projectecho
usermod -aG sudo projectecho
su - projectecho
```

#### 3. Déployer l'Application

```bash
# Cloner le repository
cd /home/projectecho
git clone https://github.com/yourusername/project-echo-orchestration.git
cd project-echo-orchestration

# Configuration Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Créer le fichier .env
cat > .env << EOF
DATABASE_URL=postgresql://projectecho:password@localhost/projectecho
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket
S3_ENDPOINT_URL=nyc3.digitaloceanspaces.com
ENCRYPTION_KEY=your-32-char-encryption-key
CORS_ORIGINS=http://your-domain.com
ENVIRONMENT=production
EOF

# Configuration Frontend
cd ../frontend
pnpm install
cat > .env << EOF
VITE_API_BASE_URL=http://your-backend-domain.com
EOF
pnpm build
```

#### 4. Configuration PostgreSQL

```bash
# En tant que root ou avec sudo
sudo -u postgres psql

# Dans PostgreSQL
CREATE DATABASE projectecho;
CREATE USER projectecho WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE projectecho TO projectecho;
\q

# Exécuter les migrations
cd /home/projectecho/project-echo-orchestration/backend
source venv/bin/activate
alembic upgrade head
```

#### 5. Configuration Nginx

```bash
# Créer la configuration Nginx
sudo nano /etc/nginx/sites-available/projectecho

# Contenu:
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /home/projectecho/project-echo-orchestration/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Activer le site
sudo ln -s /etc/nginx/sites-available/projectecho /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. Configuration Systemd (Service Backend)

```bash
# Créer le service
sudo nano /etc/systemd/system/projectecho.service

# Contenu:
[Unit]
Description=Project Echo Backend
After=network.target

[Service]
User=projectecho
WorkingDirectory=/home/projectecho/project-echo-orchestration/backend
Environment="PATH=/home/projectecho/project-echo-orchestration/backend/venv/bin"
ExecStart=/home/projectecho/project-echo-orchestration/backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# Démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable projectecho
sudo systemctl start projectecho
```

#### 7. Configuration SSL (Let's Encrypt - Gratuit)

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d your-domain.com

# Le renouvellement automatique est configuré
```

## Configuration Post-Déploiement

### 1. Accéder à l'Interface

1. Ouvrez votre navigateur: `https://your-domain.com`
2. Vous devriez voir le Dashboard

### 2. Ajouter une Chaîne YouTube

1. **Via l'Interface:**
   - Allez dans "Channels" > "Add Channel"
   - Remplissez les informations:
     - Nom de la chaîne
     - YouTube Channel ID
     - Credentials OAuth 2.0 (client_id, client_secret, refresh_token)
     - Configuration de publication
     - Filtres de contenu

2. **Configuration OAuth 2.0:**
   - Le système stocke les credentials de manière chiffrée
   - Chaque chaîne a ses propres credentials
   - Le refresh token permet de publier automatiquement

### 3. Configurer le Scraping

1. **Sources de Vidéos:**
   - Le système peut scraper depuis YouTube, TikTok, etc.
   - Configurez les sources dans les filtres de contenu
   - Définissez les critères (résolution, vues, etc.)

### 4. Configurer les Effets de Transformation

1. **Créer un Preset:**
   - Allez dans "Settings" > "Presets"
   - Créez un preset avec vos effets préférés
   - Ajustez: brightness, contrast, saturation, blur, etc.

### 5. Configurer la Planification

1. **Planification par Chaîne:**
   - Allez dans "Channels" > [Votre Chaîne] > "Configuration"
   - Configurez:
     - Fréquence (daily, weekly, custom)
     - Heures de publication
     - Timezone

2. **Voir le Calendrier:**
   - Allez dans "Calendar"
   - Visualisez les publications planifiées
   - Détectez les conflits

### 6. Activer Phase 2 (Promotion Musicale)

1. **Uploader votre Musique:**
   - Allez dans "Settings" > "Music"
   - Upload votre fichier audio (MP3, WAV, etc.)
   - Le système valide et stocke dans Spaces

2. **Activer Phase 2:**
   - Allez dans "Settings" > "Phase 2"
   - Sélectionnez les chaînes
   - Sélectionnez la musique
   - Cliquez "Activate Phase 2"
   - Les nouvelles vidéos utiliseront votre musique

## Utilisation Quotidienne

### Workflow Automatique

1. **Le système fonctionne automatiquement:**
   - Scrape des vidéos selon les filtres
   - Télécharge et transforme
   - Publie selon le planning
   - Remplace l'audio si Phase 2 est activé

2. **Monitoring:**
   - Dashboard: Vue d'ensemble du système
   - Queue: Suivi des jobs de traitement
   - Calendar: Planning des publications
   - Statistics: Performance des chaînes
   - Analytics: Métriques de promotion musicale

### Actions Manuelles

1. **Forcer une Publication:**
   - Allez dans "Queue"
   - Sélectionnez une vidéo
   - Cliquez "Publish Now"

2. **Modifier une Vidéo:**
   - Allez dans "Queue"
   - Sélectionnez une vidéo
   - Modifiez les métadonnées ou réappliquez des effets

3. **Gérer les Créateurs:**
   - Allez dans "Settings" > "Attribution"
   - Ajoutez des attributions de créateurs
   - Exportez la liste

## Maintenance

### Mises à Jour

```bash
# Sur le serveur
cd /home/projectecho/project-echo-orchestration
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart projectecho

# Frontend
cd ../frontend
pnpm install
pnpm build
sudo systemctl reload nginx
```

### Sauvegardes

1. **Base de Données:**
   ```bash
   # Backup quotidien (ajoutez dans crontab)
   0 2 * * * pg_dump -U projectecho projectecho > /backup/db-$(date +\%Y\%m\%d).sql
   ```

2. **Configuration:**
   - Exportez la configuration depuis "Settings" > "Backup"
   - Stockez dans un endroit sûr

### Monitoring

1. **Logs Backend:**
   ```bash
   sudo journalctl -u projectecho -f
   ```

2. **Logs Nginx:**
   ```bash
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

## Coûts Estimés (DigitalOcean)

### Avec App Platform:
- App Platform Basic: $5/mois
- PostgreSQL Managed: $15/mois
- Spaces (250GB): $5/mois
- **Total: $25/mois** = Gratuit pendant 1 an avec $200

### Avec Droplet:
- Droplet Basic ($6/mois): Tout inclus
- Spaces (250GB): $5/mois
- **Total: $11/mois** = Gratuit pendant ~18 mois avec $200

### Après épuisement des crédits:
- Option Droplet: $11/mois (très économique)
- Option App Platform: $25/mois (plus simple)

## Dépannage

### Problèmes Courants

1. **Backend ne démarre pas:**
   ```bash
   sudo systemctl status projectecho
   sudo journalctl -u projectecho -n 50
   ```

2. **Erreurs de connexion à la base de données:**
   - Vérifiez `DATABASE_URL` dans `.env`
   - Vérifiez que PostgreSQL est démarré: `sudo systemctl status postgresql`

3. **Erreurs S3/Spaces:**
   - Vérifiez les credentials dans `.env`
   - Vérifiez la configuration CORS sur Spaces

4. **Frontend ne charge pas:**
   - Vérifiez `VITE_API_BASE_URL` dans `.env`
   - Vérifiez les logs Nginx

## Support

Pour plus d'aide:
- Documentation: `docs/`
- Architecture: `docs/architecture.md`
- PRD: `docs/prd.md`

## Prochaines Étapes

1. **Déployer sur DigitalOcean** (suivez Option A ou B ci-dessus)
2. **Configurer votre première chaîne**
3. **Tester avec une vidéo**
4. **Activer Phase 2** quand vos chaînes sont prêtes
5. **Monitorer les analytics** pour optimiser

Bon déploiement ! 🚀
