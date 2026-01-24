# 📋 Résumé de Déploiement - Project Echo

## 🎯 En 3 Étapes Simples

### 1️⃣ Préparation (15 min)

**A. YouTube API:**
- Google Cloud Console → Créer projet → Activer YouTube Data API v3
- Créer OAuth 2.0 credentials (Desktop app)
- Exécuter: `python backend/scripts/setup_youtube_oauth.py credentials.json`
- Noter le `refresh_token`

**B. DigitalOcean Spaces:**
- Créer un Space → Noter: Access Key, Secret Key, Bucket Name, Endpoint
- Configurer CORS (Settings > CORS)

### 2️⃣ Déploiement (30 min)

**Option A: App Platform (Recommandé) ⭐**
- DigitalOcean > App Platform > Create App
- Connecter GitHub
- Backend: Web Service, `/backend`, `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- Database: PostgreSQL 15
- Frontend: Static Site, `/frontend`, `npm install && npm run build`
- **Variables d'environnement:**
  ```
  S3_ACCESS_KEY=<spaces-key>
  S3_SECRET_KEY=<spaces-secret>
  S3_BUCKET_NAME=<bucket-name>
  S3_ENDPOINT_URL=<region>.digitaloceanspaces.com
  ENCRYPTION_KEY=<32-caractères-aléatoires>
  CORS_ORIGINS=https://your-frontend-url.ondigitalocean.app
  ```
- Cliquer "Create" → Attendre 5-10 min → ✅

**Option B: Droplet ($11/mois)**
- Voir guide complet: `docs/DEPLOYMENT.md`

### 3️⃣ Configuration (10 min)

1. Ouvrir: `https://your-frontend-url.ondigitalocean.app`
2. **Channels** > **Add Channel**
3. Remplir: Nom, YouTube Channel ID, OAuth credentials
4. Configurer: Schedule, Filters, Metadata
5. **Activate** → Le système fonctionne automatiquement!

## 💰 Coûts

- **App Platform**: $25/mois = **GRATUIT 1 an** avec $200
- **Droplet**: $11/mois = **GRATUIT ~18 mois** avec $200

## 📚 Documentation Complète

- **Guide de démarrage**: [docs/GETTING_STARTED.md](GETTING_STARTED.md) ⭐
- **Déploiement détaillé**: [docs/DEPLOYMENT.md](DEPLOYMENT.md)
- **Guide d'utilisation**: [docs/USAGE_GUIDE.md](USAGE_GUIDE.md)
- **Checklist**: [docs/CHECKLIST_DEPLOYMENT.md](CHECKLIST_DEPLOYMENT.md)

## ✅ Checklist Rapide

- [ ] YouTube API configurée
- [ ] DigitalOcean Spaces créé
- [ ] Application déployée
- [ ] Première chaîne ajoutée
- [ ] Test réussi

**C'est tout ! 🚀**
