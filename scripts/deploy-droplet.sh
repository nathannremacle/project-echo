#!/bin/bash
# Script de déploiement automatique sur DigitalOcean Droplet

set -e

# Configuration
DROPLET_IP="${DROPLET_IP:-}"
DOMAIN="${DOMAIN:-}"
GITHUB_REPO="${GITHUB_REPO:-}"

if [ -z "$DROPLET_IP" ]; then
    echo "❌ Erreur: DROPLET_IP n'est pas défini"
    echo "Usage: DROPLET_IP=your-ip DOMAIN=your-domain.com ./deploy-droplet.sh"
    exit 1
fi

echo "🚀 Déploiement sur Droplet: $DROPLET_IP"

# Copier le script de setup
echo "📦 Copie du script de setup..."
scp scripts/setup-server.sh root@$DROPLET_IP:/root/setup-server.sh

# Exécuter le setup
echo "⚙️  Exécution du setup..."
ssh root@$DROPLET_IP "bash /root/setup-server.sh"

echo "✅ Déploiement terminé!"
echo "📝 N'oubliez pas de configurer:"
echo "   1. backend/.env avec vos credentials"
echo "   2. frontend/.env avec votre URL backend"
echo "   3. SSL avec: certbot --nginx -d $DOMAIN"
