# Checklist de Déploiement - Project Echo

## ✅ Pré-Déploiement

### Comptes et Services

- [ ] Compte GitHub créé
- [ ] Repository GitHub créé et code pushé
- [ ] Compte DigitalOcean créé ($200 de crédits disponibles)
- [ ] Compte Google Cloud créé (pour YouTube API)
- [ ] YouTube Data API v3 activée
- [ ] OAuth 2.0 credentials créés (Desktop app)
- [ ] Refresh token obtenu pour chaque chaîne YouTube

### Configuration YouTube API

- [ ] Projet Google Cloud créé
- [ ] YouTube Data API v3 activée
- [ ] OAuth 2.0 Client ID créé (Desktop app)
- [ ] Fichier credentials.json téléchargé
- [ ] Script `setup_youtube_oauth.py` exécuté
- [ ] Refresh tokens obtenus et notés

### Configuration DigitalOcean Spaces

- [ ] Space créé sur DigitalOcean
- [ ] Access Key noté
- [ ] Secret Key noté
- [ ] Bucket name noté
- [ ] Endpoint URL noté (ex: `nyc3.digitaloceanspaces.com`)
- [ ] CORS configuré sur le Space

## 🚀 Déploiement

### Option A: App Platform (Recommandé)

- [ ] App Platform créé sur DigitalOcean
- [ ] Repository GitHub connecté
- [ ] Component Backend configuré:
  - [ ] Source: `/` (racine du dépôt, pas `/backend`) — requis pour le module `shared`
  - [ ] Build command: `cd backend && pip install -r requirements.txt`
  - [ ] Run command: `sh backend/start.sh`
  - [ ] Environment variables configurées
- [ ] Component Database ajouté (PostgreSQL)
- [ ] Component Frontend configuré:
  - [ ] Source: `/frontend`
  - [ ] Build command: `npm install && npm run build`
  - [ ] Output directory: `dist`
  - [ ] Environment variables configurées
- [ ] Déploiement réussi
- [ ] URLs backend et frontend notées

### Option B: Droplet

- [ ] Droplet créé (Ubuntu 22.04, $6/mois)
- [ ] SSH key configurée
- [ ] Script `setup-server.sh` exécuté
- [ ] Repository cloné sur le serveur
- [ ] Backend configuré:
  - [ ] Virtual environment créé
  - [ ] Dependencies installées
  - [ ] Fichier `.env` créé avec toutes les variables
- [ ] Frontend configuré:
  - [ ] Dependencies installées
  - [ ] Fichier `.env` créé
  - [ ] Build exécuté (`pnpm build`)
- [ ] PostgreSQL configuré:
  - [ ] Database créée
  - [ ] User créé
  - [ ] Migrations exécutées (`alembic upgrade head`)
- [ ] Nginx configuré:
  - [ ] Configuration créée
  - [ ] Site activé
  - [ ] Test de configuration réussi
- [ ] Systemd service créé:
  - [ ] Service `projectecho.service` créé
  - [ ] Service démarré et activé
- [ ] SSL configuré (Let's Encrypt):
  - [ ] Certbot installé
  - [ ] Certificat obtenu
  - [ ] Nginx configuré pour HTTPS

## 🔧 Configuration Post-Déploiement

### Accès à l'Interface

- [ ] Frontend accessible via URL
- [ ] Backend API accessible via URL
- [ ] Dashboard s'affiche correctement
- [ ] Pas d'erreurs dans la console navigateur

### Première Chaîne

- [ ] Chaîne YouTube ajoutée via l'interface
- [ ] OAuth credentials configurés
- [ ] Configuration de publication définie
- [ ] Filtres de contenu configurés
- [ ] Metadata template configuré
- [ ] Chaîne activée
- [ ] Test de scraping réussi
- [ ] Test de download réussi
- [ ] Test de transformation réussi
- [ ] Test de publication réussi

### Phase 2 (Optionnel - Plus Tard)

- [ ] Musique uploadée
- [ ] Phase 2 activée pour les chaînes
- [ ] Test de remplacement audio réussi
- [ ] Vérification que les vidéos utilisent la musique

## 📊 Monitoring

### Vérifications Initiales

- [ ] Dashboard affiche les bonnes statistiques
- [ ] Queue fonctionne et affiche les jobs
- [ ] Calendar affiche le planning
- [ ] Statistics affiche les données
- [ ] Analytics fonctionne (si Phase 2 activé)
- [ ] Settings accessibles

### Logs et Debugging

- [ ] Logs backend accessibles
- [ ] Logs Nginx accessibles
- [ ] Pas d'erreurs critiques dans les logs
- [ ] Monitoring configuré (optionnel)

## 🔒 Sécurité

- [ ] Tous les secrets dans les variables d'environnement
- [ ] Pas de credentials dans le code
- [ ] SSL/HTTPS configuré
- [ ] CORS configuré correctement
- [ ] Encryption key générée (32 caractères aléatoires)
- [ ] Credentials OAuth stockés de manière sécurisée

## 💾 Sauvegardes

- [ ] Stratégie de backup définie
- [ ] Backup automatique de la base de données configuré (crontab)
- [ ] Export de configuration effectué
- [ ] Credentials sauvegardés de manière sécurisée

## ✅ Tests Finaux

- [ ] Workflow complet testé (scrape → download → transform → publish)
- [ ] Phase 2 testé (si activé)
- [ ] Multi-chaînes testé (si plusieurs chaînes)
- [ ] Gestion d'erreurs testée
- [ ] Performance acceptable

## 📝 Documentation

- [ ] URLs notées (backend, frontend)
- [ ] Credentials sauvegardés de manière sécurisée
- [ ] Configuration documentée
- [ ] Procédures de maintenance documentées

## 🎉 Prêt!

Une fois toutes les cases cochées, votre système est opérationnel!

**Prochaines étapes:**
1. Monitorer le Dashboard quotidiennement
2. Ajuster les filtres selon les résultats
3. Optimiser les heures de publication
4. Activer Phase 2 quand les chaînes sont prêtes
5. Analyser les résultats dans Analytics

**Support:**
- Guide d'utilisation: `docs/USAGE_GUIDE.md`
- Guide de déploiement: `docs/DEPLOYMENT.md`
- Architecture: `docs/architecture.md`
