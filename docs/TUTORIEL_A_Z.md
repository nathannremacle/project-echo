# Tutoriel A à Z - Project Echo

Guide complet pour comprendre et utiliser Project Echo, de l'ajout d'une chaîne YouTube jusqu'à la publication de vidéos.

---

## 1. Comment fonctionne le système

### Architecture en bref

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Base de    │
│  (React)    │     │  (FastAPI)  │     │  données    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │
       │                    ├──▶ YouTube API (publication)
       │                    ├──▶ S3/Spaces (stockage vidéos)
       │                    └──▶ GitHub (orchestration multi-repo)
       │
       └──▶ Interface web : Dashboard, Chaînes, Queue, etc.
```

- **Frontend** : Interface utilisateur (React + MUI)
- **Backend** : API REST (FastAPI) qui gère les chaînes, vidéos, jobs, orchestration
- **Base de données** : Chaînes, vidéos, jobs, configuration, etc.

### Flux de travail typique

1. **Ajouter une chaîne** → La chaîne est enregistrée dans la base
2. **Configurer la chaîne** → Filtres, planning, templates
3. **Activer la chaîne** → Elle peut recevoir des vidéos
4. **Scraping** → Le système trouve des vidéos sources (YouTube, TikTok, etc.)
5. **Download** → Téléchargement des vidéos
6. **Transformation** → Effets, montage, remplacement audio (Phase 2)
7. **Publication** → Mise en ligne sur YouTube selon le planning

---

## 2. Première connexion à l'interface

### Accéder à l'application

- **En local** : `http://localhost:3000` (frontend) ou `http://localhost:8000` (backend)
- **En production** : URL de votre déploiement DigitalOcean

### Navigation principale

| Menu | Rôle |
|------|------|
| **Dashboard** | Vue d'ensemble : chaînes, statut système, activité récente |
| **Channels** | Liste des chaînes, ajout, configuration |
| **Queue** | Jobs et vidéos en cours de traitement |
| **Calendar** | Planning des publications |
| **Statistics** | Statistiques globales et par chaîne |
| **Analytics** | Métriques Phase 2, ROI, recommandations |
| **Settings** | Configuration système, presets, musique |

---

## 3. Ajouter une chaîne YouTube (étape par étape)

### Option A : Chaîne de test (démarrage rapide)

Pour tester l’interface sans configurer YouTube :

1. Aller dans **Channels**
2. Cliquer sur **« Ajouter une chaîne de test »**
3. Une chaîne fictive est créée (credentials placeholder)
4. Elle apparaît sur le Dashboard et dans la liste des chaînes

**Limite** : cette chaîne ne peut pas publier sur YouTube (credentials factices).

---

### Option B : Chaîne YouTube réelle

#### Étape 1 : Trouver le YouTube Channel ID

Le **YouTube Channel ID** est un identifiant unique (format `UC` + 22 caractères).

**Méthode 1 – Depuis l’URL de la chaîne**

1. Ouvrir votre chaîne YouTube
2. Regarder l’URL :
   - `https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxxxxx` → l’ID est la partie après `/channel/`
   - `https://www.youtube.com/@MonNom` → il faut récupérer l’ID autrement

**Méthode 2 – YouTube Studio**

1. Aller sur [YouTube Studio](https://studio.youtube.com/)
2. **Paramètres** (icône engrenage) → **Chaîne** → **Paramètres avancés**
3. L’**ID de la chaîne** est affiché en bas de page

**Méthode 3 – À partir d’une vidéo**

1. Ouvrir une vidéo de votre chaîne
2. Cliquer sur le nom de la chaîne
3. L’URL de la chaîne contient l’ID : `youtube.com/channel/UC...`

**Exemple** : `UC_x5XG1OV2P6uZZ5FSM9Ttw` (chaîne de test Google)

#### Étape 2 : Créer la chaîne dans l’interface

1. Aller dans **Channels**
2. Cliquer sur **« Ajouter une chaîne »**
3. Remplir le formulaire :

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Nom de la chaîne** | Nom affiché dans l’app | Ma Chaîne Edit |
| **YouTube Channel ID** | ID trouvé à l’étape 1 | UC_x5XG1OV2P6uZZ5FSM9Ttw |
| **URL YouTube** (optionnel) | URL complète | https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw |

4. Cliquer sur **Créer**

**Important** : avec cette option, les credentials sont des placeholders. Pour publier réellement sur YouTube, il faut configurer OAuth (voir section 4).

#### Étape 3 : Configurer la chaîne

1. Cliquer sur la carte de la chaîne
2. Sur la page de détail, modifier :
   - **Posting Schedule** : fréquence, heures, fuseau
   - **Content Filters** : résolution min, vues min, watermark
   - **Metadata Template** : templates de titre, description, tags
3. Cliquer sur **Save**

#### Étape 4 : Activer la chaîne

1. Sur la page de détail de la chaîne
2. Activer le switch **« Activate »**
3. La chaîne devient active et peut recevoir des vidéos

---

## 4. Configurer OAuth pour publier sur YouTube (avancé)

Pour publier réellement sur YouTube, il faut des credentials OAuth 2.0.

### Créer un projet Google Cloud

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un projet (ou en sélectionner un)
3. Activer **YouTube Data API v3** : APIs & Services → Library → YouTube Data API v3 → Enable

### Créer des credentials OAuth

1. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**
2. Type : **Desktop app**
3. Télécharger le fichier JSON (client_id, client_secret)

### Obtenir le Refresh Token

```bash
cd backend
python scripts/setup_youtube_oauth.py path/to/credentials.json
```

1. Une fenêtre de navigateur s’ouvre
2. Se connecter au compte YouTube de la chaîne
3. Autoriser l’accès
4. Le script affiche le **refresh_token** à copier

### Configurer la chaîne avec les vrais credentials

Actuellement, l’interface ne permet pas de saisir les credentials OAuth. Il faut soit :

- Utiliser l’API backend pour mettre à jour les credentials
- Ou attendre une future évolution de l’interface

---

## 5. Utiliser le Dashboard

### Vue d’ensemble

- **System Statistics** : statut orchestration, queue, etc.
- **Channels** : nombre de chaînes actives / total
- **Chaînes** : cartes cliquables vers chaque chaîne
- **Quick Actions** : Start/Stop, Pause/Resume, Add Channel
- **Recent Activity** : publications, statut système, erreurs réelles

### Messages affichés

| Message | Signification |
|---------|---------------|
| **Orchestration system stopped** | État par défaut, pas une erreur |
| **No GitHub repository configured** | Chaîne sans dépôt GitHub (normal pour une chaîne de test) |
| **X videos published** | Publications récentes |

---

## 6. Gérer la file de traitement (Queue)

### Vue Queue

- **Jobs** : scrape, download, transform, publish
- **Videos** : vidéos en attente ou en cours
- **Filtres** : statut, chaîne, type de job

### Actions possibles

- **Retry** : relancer un job échoué
- **Cancel** : annuler un job en file
- **Delete** : supprimer une vidéo

---

## 7. Planning (Calendar)

- Planning des publications
- Filtres : chaîne, vidéo, statut, dates
- Actions : modifier, annuler une publication planifiée

---

## 8. Paramètres (Settings)

### Configuration système

- **Config** : paramètres globaux
- **Transformation Presets** : effets (brightness, contrast, etc.)
- **Music** : pistes audio pour Phase 2
- **Phase 2** : activation de la promotion musicale

### Presets de transformation

1. **Settings** → **Transformation Presets**
2. **Create Preset** : nom, description, effets
3. Associer le preset à une chaîne dans sa configuration

---

## 9. Récapitulatif du flux complet

```
1. Déployer l'app (DigitalOcean)
2. Exécuter seed_db.py → chaîne de test créée
3. Se connecter au Dashboard
4. Channels → Ajouter une chaîne (test ou réelle)
5. Cliquer sur la chaîne → Configurer → Activer
6. (Optionnel) Settings → Phase 2 → Activer
7. (Optionnel) Démarrer l'orchestration (Quick Actions)
8. Surveiller Queue et Calendar
```

---

## 10. FAQ rapide

**Où trouver mon YouTube Channel ID ?**  
→ YouTube Studio → Paramètres → Chaîne → Paramètres avancés

**Pourquoi "No GitHub repository configured" ?**  
→ C’est un avertissement pour les chaînes sans dépôt GitHub. Pas bloquant pour une chaîne de test.

**Comment publier vraiment sur YouTube ?**  
→ Configurer OAuth (Google Cloud + script `setup_youtube_oauth.py`) et mettre à jour les credentials de la chaîne.

**La chaîne de test peut-elle publier ?**  
→ Non, elle utilise des credentials factices. Elle sert à tester l’interface.

**Comment supprimer une chaîne ?**  
→ Actuellement via l’API ou la base de données. L’interface de suppression n’est pas encore exposée.

---

## Ressources

- [QUICK_START.md](./QUICK_START.md) – Déploiement
- [USAGE_GUIDE.md](./USAGE_GUIDE.md) – Guide d’utilisation détaillé
- [architecture.md](./architecture.md) – Architecture technique
