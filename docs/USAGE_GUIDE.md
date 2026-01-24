# Guide d'Utilisation - Project Echo

## Vue d'ensemble

Project Echo automatise complètement le processus de création, transformation et publication de vidéos sur plusieurs chaînes YouTube. Ce guide vous explique comment utiliser le système une fois déployé.

## Interface Utilisateur

### Dashboard

Le Dashboard est votre point d'entrée principal. Il affiche:
- **Statut du système**: Running/Paused
- **Statistiques globales**: Nombre de chaînes, vidéos, vues
- **Chaînes actives**: Liste avec statut et métriques
- **Actions rapides**: Pause/Resume, ajouter une chaîne
- **Activité récente**: Dernières publications et événements

### Navigation

- **Dashboard**: Vue d'ensemble
- **Channels**: Gestion des chaînes YouTube
- **Queue**: File de traitement des vidéos
- **Calendar**: Planning des publications
- **Statistics**: Statistiques détaillées
- **Analytics**: Analytics de promotion musicale
- **Settings**: Configuration système

## Ajouter une Chaîne YouTube

### Étape 1: Préparer les Credentials OAuth 2.0

1. **Créer un projet Google Cloud:**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un nouveau projet
   - Activez "YouTube Data API v3"

2. **Créer OAuth 2.0 Credentials:**
   - APIs & Services > Credentials
   - Create Credentials > OAuth 2.0 Client ID
   - Application type: Desktop app
   - Téléchargez le fichier JSON

3. **Obtenir le Refresh Token:**
   ```bash
   cd backend
   python scripts/setup_youtube_oauth.py path/to/credentials.json
   ```
   - Une fenêtre de navigateur s'ouvrira
   - Autorisez l'accès à votre compte YouTube
   - Notez le `refresh_token` affiché

### Étape 2: Ajouter la Chaîne dans l'Interface

1. Allez dans **Channels** > **Add Channel**
2. Remplissez le formulaire:
   - **Name**: Nom d'affichage (ex: "My Edit Channel")
   - **YouTube Channel ID**: Trouvable dans l'URL de votre chaîne
     - Format: `UCxxxxxxxxxxxxxxxxxxxxxxxxxx`
     - Ou dans YouTube Studio > Settings > Channel > Advanced
   - **OAuth Credentials**:
     - Client ID: Depuis Google Cloud
     - Client Secret: Depuis Google Cloud
     - Refresh Token: Depuis le script OAuth

3. **Configuration de Publication:**
   - **Frequency**: Daily, Weekly, ou Custom
   - **Preferred Times**: Heures de publication (ex: "10:00, 18:00")
   - **Timezone**: Votre fuseau horaire

4. **Filtres de Contenu:**
   - **Min Resolution**: 720p, 1080p, 1440p, ou 2160p
   - **Min Views**: Nombre minimum de vues pour considérer une vidéo "virale"
   - **Exclude Watermarked**: Exclure les vidéos avec watermark

5. **Metadata Template:**
   - **Title Template**: Template pour les titres (ex: "{sourceTitle} | Edit")
   - **Description Template**: Template pour les descriptions
   - **Default Tags**: Tags par défaut (séparés par virgules)

6. Cliquez **Save**

### Étape 3: Activer la Chaîne

1. Allez dans **Channels** > [Votre Chaîne]
2. Cliquez sur le toggle **Activate** en haut
3. La chaîne commencera à scraper et publier automatiquement

## Workflow Automatique

Une fois activée, une chaîne fonctionne automatiquement:

1. **Scraping** (toutes les X heures):
   - Le système cherche des vidéos selon vos filtres
   - Scrape depuis YouTube, TikTok, etc.
   - Enregistre les métadonnées

2. **Download** (automatique):
   - Télécharge les vidéos sélectionnées
   - Stocke dans DigitalOcean Spaces (S3)

3. **Transformation** (automatique):
   - Applique les effets configurés
   - Rend la vidéo "unique" pour éviter la détection
   - Stocke la version transformée

4. **Publication** (selon planning):
   - Publie automatiquement selon le planning
   - Utilise les métadonnées du template
   - Si Phase 2 activé: remplace l'audio par votre musique

## Gérer les Vidéos

### Vue Queue

La page **Queue** affiche toutes les vidéos en traitement:

- **Filtres**: Par statut, chaîne, type de job
- **Actions**:
  - **Retry**: Réessayer un job échoué
  - **Cancel**: Annuler un job en cours
  - **Delete**: Supprimer une vidéo
  - **Preview**: Voir les détails (à venir)

### Actions Manuelles

1. **Forcer une Publication:**
   - Queue > Sélectionnez une vidéo
   - Cliquez "Publish Now"

2. **Réappliquer des Effets:**
   - Queue > Sélectionnez une vidéo
   - Modifiez le preset de transformation
   - Cliquez "Retry"

## Planification

### Vue Calendar

La page **Calendar** montre le planning des publications:

- **Vues**: Day, Week, Month
- **Conflits**: Détecte les publications simultanées
- **Actions**:
  - Cliquer sur un événement pour voir les détails
  - Reschedule: Changer la date/heure
  - Cancel: Annuler une publication

### Configuration de Planning

1. Allez dans **Channels** > [Votre Chaîne] > **Configuration**
2. **Posting Schedule**:
   - **Frequency**: Daily, Weekly, Custom
   - **Preferred Times**: Heures (format 24h, séparées par virgules)
   - **Timezone**: Fuseau horaire
   - **Days of Week**: Pour "Weekly" (0=Dimanche, 6=Samedi)

## Phase 2: Promotion Musicale

### Étape 1: Uploader votre Musique

1. Allez dans **Settings** > **Music**
2. Cliquez **Upload Music**
3. Sélectionnez votre fichier audio:
   - Formats supportés: MP3, WAV, M4A, FLAC
   - Taille max: 100MB (configurable)
   - Durée: Aucune limite
4. Remplissez les métadonnées:
   - **Name**: Nom de la track
   - **Artist**: Votre nom d'artiste
5. Cliquez **Upload**

### Étape 2: Activer Phase 2

1. Allez dans **Settings** > **Phase 2**
2. Vérifiez le statut (doit montrer vos chaînes)
3. **Configuration**:
   - **Select Channels**: Toutes ou spécifiques
   - **Music Track**: Sélectionnez votre musique
   - **Options**:
     - ✅ Apply to already published videos (retroactive)
     - ✅ Normalize audio levels
     - ✅ Loop audio if shorter than video
4. Cliquez **Activate Phase 2**

### Résultat

- Toutes les nouvelles vidéos utiliseront votre musique
- Les vidéos existantes seront mises à jour si "retroactive" est activé
- Vous pouvez suivre l'efficacité dans **Analytics**

## Analytics & Statistiques

### Statistics Page

Affiche:
- **Overview**: KPIs globaux (subscribers, views, videos)
- **Channel Breakdown**: Statistiques par chaîne
- **Growth Trends**: Graphiques de croissance
- **Anomaly Detection**: Alertes sur changements importants

### Analytics Page (Phase 2)

Affiche:
- **Music Promotion Metrics**: Vidéos avec musique, vues
- **Wave Effect**: Publications simultanées, portée
- **Phase 2 Comparison**: Avant/après Phase 2
- **ROI**: Efficacité de la promotion
- **Insights**: Détections automatiques
- **Recommendations**: Suggestions d'optimisation

## Gestion des Créateurs

### Attribution

1. Allez dans **Settings** > **Attribution**
2. **Liste des Créateurs**: Voir tous les créateurs détectés
3. **Attribuer une Vidéo**:
   - Sélectionnez une vidéo
   - Entrez le nom du créateur
   - Optionnel: URL de la chaîne du créateur
   - Cliquez **Save**

4. **Attribution en Masse**:
   - Sélectionnez plusieurs vidéos
   - Entrez le créateur
   - Cliquez **Bulk Attribute**

## Configuration Système

### Settings > General

- **Default Effect Preset**: Preset utilisé par défaut
- **Video Quality**: Qualité de traitement
- **Auto-publish**: Publier automatiquement après transformation

### Settings > Processing

- **Queue Size**: Taille maximale de la file
- **Parallel Processing**: Nombre de jobs simultanés
- **Retry Attempts**: Nombre de tentatives en cas d'échec
- **Retry Delay**: Délai entre les tentatives

### Settings > Presets

- **Créer un Preset**:
  - Cliquez "Create Preset"
  - Configurez les effets:
    - Brightness, Contrast, Saturation, Hue
    - Blur, Sharpen, Noise Reduction
    - Flip (horizontal/vertical)
  - Sauvegardez

### Settings > Backup

- **Export**: Télécharge toute la configuration en JSON
- **Import**: Restaure depuis un fichier JSON

## Monitoring & Maintenance

### Vérifier le Statut

1. **Dashboard**: Vue d'ensemble rapide
2. **Queue**: Voir les jobs en cours
3. **Logs** (sur serveur):
   ```bash
   sudo journalctl -u projectecho -f
   ```

### Problèmes Courants

1. **Vidéo ne se publie pas:**
   - Vérifiez les credentials OAuth dans Channel > Configuration
   - Vérifiez les logs: Queue > Voir les erreurs
   - Vérifiez que la chaîne est "Active"

2. **Erreurs de transformation:**
   - Vérifiez que FFmpeg est installé sur le serveur
   - Vérifiez les logs backend
   - Vérifiez l'espace disque

3. **Erreurs S3/Spaces:**
   - Vérifiez les credentials dans Settings
   - Vérifiez la configuration CORS sur Spaces
   - Vérifiez les permissions du bucket

## Bonnes Pratiques

1. **Commencez Petit:**
   - Testez avec 1-2 chaînes d'abord
   - Vérifiez que tout fonctionne
   - Ajoutez progressivement

2. **Monitorer Régulièrement:**
   - Vérifiez le Dashboard quotidiennement
   - Surveillez les erreurs dans Queue
   - Consultez les Analytics hebdomadairement

3. **Optimiser les Filtres:**
   - Ajustez les filtres de contenu selon les résultats
   - Testez différents presets d'effets
   - Optimisez les heures de publication

4. **Phase 2 Timing:**
   - Attendez que vos chaînes aient une base d'abonnés
   - Activez Phase 2 quand vous êtes prêt à promouvoir
   - Monitorer l'impact dans Analytics

5. **Sauvegardes:**
   - Exportez la configuration régulièrement
   - Sauvegardez la base de données
   - Gardez une copie des credentials

## Support

- **Documentation**: `docs/`
- **Architecture**: `docs/architecture.md`
- **Déploiement**: `docs/DEPLOYMENT.md`
- **PRD**: `docs/prd.md`

## FAQ

**Q: Combien de chaînes puis-je gérer?**
R: Aucune limite technique. Le système peut gérer des dizaines de chaînes.

**Q: Puis-je utiliser mes propres vidéos?**
R: Oui, vous pouvez uploader vos propres vidéos via l'API ou l'interface (à venir).

**Q: Combien coûte le stockage?**
R: DigitalOcean Spaces: $5/mois pour 250GB. Assez pour des milliers de vidéos.

**Q: Les vidéos sont-elles vraiment "uniques"?**
R: Oui, les transformations (color grading, flips, effets) rendent les vidéos suffisamment différentes pour éviter la détection automatique.

**Q: Puis-je désactiver une chaîne temporairement?**
R: Oui, utilisez le toggle "Activate/Deactivate" dans Channel Detail.

**Q: Comment savoir si Phase 2 fonctionne?**
R: Vérifiez Analytics > Music Promotion Metrics et écoutez les vidéos publiées.

---

**Bon usage ! 🎬**
