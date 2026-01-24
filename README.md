# Project Echo - Central Orchestration Repository

**Project Echo** is an automated multi-channel YouTube video editing and publishing system. This central orchestration repository manages the coordination of multiple YouTube channels, each operating in its own isolated repository.

## Overview

Project Echo automates the complete pipeline of:
- Scraping high-quality edit videos from the internet
- Transforming videos with quality effects to avoid detection
- Publishing videos to multiple YouTube channels automatically
- Orchestrating multi-channel operations for viral "wave" effects
- Managing channel configurations and statistics

## Repository Structure

This is the **central orchestration repository** that contains:
- **Frontend**: React-based management interface for monitoring and controlling all channels
- **Backend**: FastAPI orchestration service for coordinating multi-channel operations
- **Shared**: Python libraries shared across channel repositories
- **Templates**: Template for creating new channel repositories

Each YouTube channel operates in its own isolated repository (`project-echo-channel-{name}`) with:
- Independent GitHub Actions workflows
- Channel-specific configuration
- Isolated GitHub Secrets for API credentials

## Quick Start

### 🚀 Déploiement Rapide (Recommandé)

**Pour déployer rapidement sur DigitalOcean (gratuit avec vos $200 de crédits):**

1. **Lisez le guide de déploiement:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
2. **Ou le guide rapide:** [docs/QUICK_START.md](docs/QUICK_START.md)

**Deux options:**
- **App Platform** ($25/mois): Le plus simple, déploiement automatique
- **Droplet** ($11/mois): Plus économique, contrôle total

### 📖 Utilisation

Une fois déployé, consultez: [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)

### 💻 Développement Local

#### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm 8+
- Git
- FFmpeg (for video processing)

#### Setup

1. **Clone this repository:**
   ```bash
   git clone <repository-url>
   cd project-echo-orchestration
   ```

2. **Set up backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend:**
   ```bash
   cd frontend
   pnpm install
   ```

4. **Configure environment:**
   - Copy `.env.example` files and fill in your configuration
   - See [Development Workflow](docs/architecture.md#development-workflow) for details

## Architecture

For detailed architecture documentation, see:
- [Full Architecture Document](docs/architecture.md)
- [Product Requirements Document](docs/prd.md)

## Multi-Repository Architecture

Project Echo uses a **multi-repository architecture**:

- **Central Repo** (this repo): Orchestration, management interface, shared libraries
- **Channel Repos**: One repository per YouTube channel with independent workflows

See [Multi-Repository Architecture Guide](docs/MULTI-REPO-ARCHITECTURE.md) for details on creating and managing channel repositories.

## Development

### Running Locally

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd frontend
pnpm dev
```

### Testing

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
pnpm test
```

## Documentation

### 🚀 Déploiement et Utilisation

- **[Guide de Démarrage](docs/GETTING_STARTED.md)** ⭐ - Commencez ici!
- **[Guide de Déploiement](docs/DEPLOYMENT.md)** - Déploiement détaillé sur DigitalOcean
- **[Guide Rapide](docs/QUICK_START.md)** - Déploiement en 15 minutes
- **[Guide d'Utilisation](docs/USAGE_GUIDE.md)** - Comment utiliser le système
- **[Checklist de Déploiement](docs/CHECKLIST_DEPLOYMENT.md)** - Checklist complète

### 📚 Technique

- [Architecture](docs/architecture.md) - Complete technical architecture
- [PRD](docs/prd.md) - Product requirements and epics
- [Multi-Repo Guide](docs/MULTI-REPO-ARCHITECTURE.md) - Channel repository setup
- [Development Workflow](docs/architecture.md#development-workflow) - Setup and commands

## Technology Stack

- **Frontend**: React 18.x, TypeScript, Vite, Material-UI, Zustand
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: SQLite (MVP) → PostgreSQL (production)
- **Video Processing**: FFmpeg, OpenCV
- **CI/CD**: GitHub Actions
- **Storage**: AWS S3 / Google Cloud Storage

## License

[Add license information]

## Contributing

[Add contributing guidelines if applicable]
