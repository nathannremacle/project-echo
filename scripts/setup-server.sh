#!/bin/bash
# Script de configuration automatique du serveur DigitalOcean Droplet

set -e

echo "🚀 Configuration du serveur Project Echo..."

# Mise à jour
echo "📦 Mise à jour du système..."
apt update && apt upgrade -y

# Installation des dépendances
echo "📦 Installation des dépendances..."
apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql ffmpeg git certbot python3-certbot-nginx

# Installation pnpm
echo "📦 Installation de pnpm..."
npm install -g pnpm

# Création utilisateur
echo "👤 Création de l'utilisateur..."
if ! id "projectecho" &>/dev/null; then
    adduser --disabled-password --gecos "" projectecho
    usermod -aG sudo projectecho
fi

# Note: Le reste du script nécessite que vous ayez cloné le repo
# et configuré les fichiers .env manuellement

echo "✅ Configuration de base terminée!"
echo "📝 Prochaines étapes:"
echo "   1. Clonez votre repository: git clone <your-repo-url>"
echo "   2. Configurez backend/.env"
echo "   3. Configurez frontend/.env"
echo "   4. Exécutez les migrations: alembic upgrade head"
echo "   5. Build le frontend: pnpm build"
echo "   6. Configurez Nginx et systemd (voir docs/DEPLOYMENT.md)"
