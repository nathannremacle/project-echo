# 🚀 Guide de Démarrage - Project Echo

## Vue d'Ensemble en 3 Étapes

1. **Déployer** → DigitalOcean (gratuit avec vos $200)
2. **Configurer** → Ajouter vos chaînes YouTube
3. **Lancer** → Le système fonctionne automatiquement

---

## 📋 Étape 1: Préparation (15 minutes)

### A. Configuration YouTube API

1. **Google Cloud Console:**
   - Allez sur https://console.cloud.google.com/
   - Créez un projet
   - Activez "YouTube Data API v3"
   - Créez OAuth 2.0 credentials (Desktop app)
   - Téléchargez le fichier `credentials.json`

2. **Obtenir Refresh Token:**
   ```bash
   cd backend
   python scripts/setup_youtube_oauth.py path/to/credentials.json
   ```
   - Une fenêtre s'ouvre → Autorisez
   - Notez le `refresh_token` affiché

### B. Configuration DigitalOcean Spaces

1. **Créer un Space:**
   - DigitalOcean > Spaces > Create Space
   - Région: Choisissez la plus proche
   - Notez: Access Key, Secret Key, Bucket Name, Endpoint

2. **Configurer CORS:**
   - Settings > CORS
   - Activez CORS avec configuration par défaut

---

## 🚀 Étape 2: Déploiement (30 minutes)

### Option A: App Platform (Le Plus Simple) ⭐ RECOMMANDÉ

**Coût: $25/mois = GRATUIT pendant 1 an**

1. **DigitalOcean App Platform:**
   - https://cloud.digitalocean.com/apps
   - "Create App" > Connectez GitHub
   - Sélectionnez votre repository

2. **Backend Component:**
   - Type: Web Service
   - Source: `/backend`
   - Build: `pip install -r requirements.txt`
   - Run: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Env Variables:**
     ```
     S3_ACCESS_KEY=<spaces-key>
     S3_SECRET_KEY=<spaces-secret>
     S3_BUCKET_NAME=<bucket-name>
     S3_ENDPOINT_URL=<region>.digitaloceanspaces.com
     ENCRYPTION_KEY=<générez-32-caractères-aléatoires>
     CORS_ORIGINS=https://your-frontend-url.ondigitalocean.app
     ```

3. **Database Component:**
   - Add Component > Database
   - Type: PostgreSQL 15
   - `DATABASE_URL` sera auto-injecté

4. **Frontend Component:**
   - Type: Static Site
   - Source: `/frontend`
   - Build: `npm install && npm run build`
   - Output: `dist`
   - **Env Variables:**
     ```
     VITE_API_BASE_URL=https://your-backend-url.ondigitalocean.app
     ```

5. **Créer & Déployer:**
   - Cliquez "Create Resources"
   - Attendez 5-10 minutes
   - ✅ C'est fait!

### Option B: Droplet (Plus Économique)

**Coût: $11/mois = GRATUIT pendant ~18 mois**

Voir le guide complet: [docs/DEPLOYMENT.md](DEPLOYMENT.md)

---

## ⚙️ Étape 3: Configuration (10 minutes)

### 1. Accéder à l'Interface

Ouvrez: `https://your-frontend-url.ondigitalocean.app`

### 2. Ajouter votre Première Chaîne

1. **Channels** > **Add Channel**
2. Remplissez:
   - **Name**: Nom d'affichage
   - **YouTube Channel ID**: Dans l'URL de votre chaîne (`UC...`)
   - **OAuth Credentials**:
     - Client ID (depuis Google Cloud)
     - Client Secret (depuis Google Cloud)
     - Refresh Token (depuis le script)
3. **Configuration:**
   - **Schedule**: Daily à 10:00, 18:00 (exemple)
   - **Filters**: Min 1080p, Min 10000 vues
   - **Metadata**: Templates pour titres/descriptions
4. **Save** puis **Activate**

### 3. Tester

- Le système va automatiquement:
  1. Scraper des vidéos
  2. Les télécharger
  3. Les transformer
  4. Les publier selon le planning

- Surveillez dans **Queue** et **Dashboard**

---

## 🎵 Phase 2: Promotion Musicale (Quand Prêt)

### 1. Uploader votre Musique

- **Settings** > **Music** > **Upload**
- Format: MP3, WAV, etc.
- Remplissez: Name, Artist

### 2. Activer Phase 2

- **Settings** > **Phase 2**
- Sélectionnez: Chaînes + Musique
- Options: Retroactive, Normalize, Loop
- **Activate**

### 3. Monitorer

- **Analytics** > Voir les métriques
- Écoutez les vidéos publiées pour vérifier

---

## 📊 Utilisation Quotidienne

### Dashboard
- Vue d'ensemble du système
- Statut des chaînes
- Statistiques globales

### Queue
- Tous les jobs de traitement
- Actions: Retry, Cancel, Delete
- Filtres par statut/chaîne

### Calendar
- Planning des publications
- Détection de conflits
- Reschedule/Cancel

### Statistics
- Performance des chaînes
- Croissance (subscribers, views)
- Tendances

### Analytics (Phase 2)
- Métriques de promotion musicale
- Effet "vague"
- ROI et recommandations

### Settings
- Configuration globale
- Presets d'effets
- Musique
- Phase 2
- Attribution créateurs
- Backup/Restore

---

## 💰 Coûts

### Avec App Platform:
- **$25/mois** = Gratuit pendant 1 an avec $200

### Avec Droplet:
- **$11/mois** = Gratuit pendant ~18 mois avec $200

### Après crédits:
- Droplet: $11/mois (très économique)
- App Platform: $25/mois (plus simple)

---

## 🔧 Maintenance

### Mises à Jour

```bash
# Sur le serveur (Droplet)
cd /home/projectecho/project-echo-orchestration
git pull
cd backend && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart projectecho
cd ../frontend && pnpm install && pnpm build
sudo systemctl reload nginx
```

### Logs

```bash
# Backend logs
sudo journalctl -u projectecho -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Sauvegardes

- **Configuration**: Settings > Backup > Export
- **Base de données**: Automatique (à configurer)

---

## 📚 Documentation Complète

- **Déploiement détaillé**: [docs/DEPLOYMENT.md](DEPLOYMENT.md)
- **Guide d'utilisation**: [docs/USAGE_GUIDE.md](USAGE_GUIDE.md)
- **Checklist**: [docs/CHECKLIST_DEPLOYMENT.md](CHECKLIST_DEPLOYMENT.md)
- **Architecture**: [docs/architecture.md](architecture.md)

---

## ✅ Checklist Rapide

- [ ] YouTube API configurée (OAuth credentials)
- [ ] DigitalOcean Spaces créé
- [ ] Application déployée (App Platform ou Droplet)
- [ ] Première chaîne ajoutée et activée
- [ ] Test de publication réussi
- [ ] Phase 2 activée (quand prêt)
- [ ] Monitoring configuré

---

## 🆘 Dépannage Rapide

**Backend ne démarre pas:**
```bash
sudo systemctl status projectecho
sudo journalctl -u projectecho -n 50
```

**Erreurs de base de données:**
- Vérifiez `DATABASE_URL` dans `.env`
- Vérifiez que PostgreSQL tourne: `sudo systemctl status postgresql`

**Erreurs S3/Spaces:**
- Vérifiez les credentials dans `.env`
- Vérifiez CORS sur Spaces

**Frontend ne charge pas:**
- Vérifiez `VITE_API_BASE_URL` dans `.env`
- Vérifiez les logs Nginx

---

## 🎯 Prochaines Étapes

1. ✅ Déployer (Option A ou B)
2. ✅ Configurer votre première chaîne
3. ✅ Tester le workflow complet
4. ✅ Monitorer les résultats
5. ✅ Optimiser les filtres et planning
6. ✅ Activer Phase 2 quand les chaînes sont prêtes
7. ✅ Analyser dans Analytics

**Bon déploiement ! 🚀**
