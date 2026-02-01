# Comment ça marche ? — Project Echo

**En bref** : Project Echo automatise la publication de vidéos sur YouTube. Vous lui donnez des sources (URLs, chaînes, mots-clés), il récupère les vidéos, les transforme si besoin, et les publie sur votre chaîne YouTube.

---

## Le flux en 5 étapes

```
  1. SCRAPER          2. TÉLÉCHARGER       3. TRANSFORMER        4. PUBLIER
  ─────────          ──────────────       ───────────────        ──────────
  Trouver des         Télécharger la       Appliquer des          Mettre en ligne
  vidéos sources     vidéo sur le         effets (optionnel)      sur YouTube
  (YouTube, etc.)    serveur
```

**En une phrase** : Le système trouve des vidéos → les télécharge → les transforme (optionnel) → les publie sur votre chaîne YouTube.

---

## Ce dont vous avez besoin

| Élément | Rôle |
|--------|------|
| **Une chaîne YouTube** | C’est là que les vidéos seront publiées |
| **Credentials OAuth** | Pour que l’app puisse publier à votre place (Google Cloud + script) |
| **Une interface web** | Dashboard, Chaînes, Queue, etc. |

**Pas besoin de** : dépôt GitHub par chaîne, configuration complexe pour démarrer.

---

## Où faire quoi dans l’interface

| Page | Utilité |
|------|---------|
| **Channels** | Créer une chaîne, configurer OAuth, lancer le pipeline |
| **Queue** | Voir les vidéos en cours, les jobs, ajouter une vidéo par URL |
| **Dashboard** | Vue d’ensemble des chaînes et du statut |
| **Settings** | Presets de transformation, musique, etc. |

---

## Comment lancer une publication ?

**Option 1 — Depuis une chaîne**

1. **Channels** → cliquer sur votre chaîne  
2. Cliquer sur **« Lancer le pipeline »**  
   → Le système scrape les sources configurées, télécharge, transforme et publie.

**Option 2 — Depuis une URL précise**

1. **Channels** → votre chaîne → **« Ajouter une vidéo (URL) »**  
   **ou**  
2. **Queue** → **« Ajouter une vidéo »** → choisir la chaîne et coller l’URL  
3. Le système scrape cette vidéo, la télécharge, la transforme et la publie.

---

## Où voir ce qui se passe ?

- **Queue → Vidéos** : liste des vidéos (scrappées, en cours, publiées)  
- **Queue → Jobs** : jobs en file (scrape, download, transform, publish)

---

## Schéma simplifié

```
                    VOUS
                     │
                     │ 1. Créez une chaîne + configurez OAuth
                     │ 2. Cliquez "Lancer le pipeline" ou "Ajouter une vidéo"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROJECT ECHO                              │
│                                                              │
│   Scrape ──▶ Download ──▶ Transform (optionnel) ──▶ Upload  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ 3. Vidéo publiée
                     ▼
              VOTRE CHAÎNE YOUTUBE
```

---

## Pour aller plus loin

- **Tutoriel détaillé** : [TUTORIEL_A_Z.md](./TUTORIEL_A_Z.md)  
- **Déploiement** : [QUICK_START.md](./QUICK_START.md)  
- **Architecture technique** : [architecture.md](./architecture.md)
