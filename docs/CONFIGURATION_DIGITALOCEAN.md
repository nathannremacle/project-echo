# Configuration DigitalOcean Spaces (S3-compatible)

## Vue d'Ensemble

DigitalOcean Spaces est compatible avec l'API S3, donc le système fonctionne directement avec boto3. Il suffit de configurer l'endpoint URL.

## Configuration

### Variables d'Environnement

Pour utiliser DigitalOcean Spaces au lieu d'AWS S3, configurez:

```bash
# Utilisez les credentials DigitalOcean Spaces
AWS_ACCESS_KEY_ID=<spaces-access-key>
AWS_SECRET_ACCESS_KEY=<spaces-secret-key>
AWS_REGION=<spaces-region>  # Ex: nyc3, sfo3, ams3
AWS_S3_BUCKET=<your-space-name>

# IMPORTANT: Ajoutez l'endpoint pour DigitalOcean Spaces
# Le système utilisera automatiquement cet endpoint si défini
S3_ENDPOINT_URL=<region>.digitaloceanspaces.com
# Ex: nyc3.digitaloceanspaces.com
```

### Exemple de Configuration Complète

```bash
# Backend .env
DATABASE_URL=postgresql://user:pass@localhost/projectecho
AWS_ACCESS_KEY_ID=DO1234567890ABCDEF
AWS_SECRET_ACCESS_KEY=abcdef1234567890ABCDEF1234567890ABCDEF
AWS_REGION=nyc3
AWS_S3_BUCKET=project-echo-videos
S3_ENDPOINT_URL=nyc3.digitaloceanspaces.com
ENCRYPTION_KEY=<générez-32-caractères-aléatoires>
CORS_ORIGINS=https://your-frontend-url.com
```

## Configuration CORS sur Spaces

1. Allez sur DigitalOcean > Spaces > [Votre Space]
2. Settings > CORS Configurations
3. Ajoutez cette configuration:

```json
{
  "AllowedOrigins": ["*"],
  "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
  "AllowedHeaders": ["*"],
  "ExposeHeaders": ["ETag"],
  "MaxAgeSeconds": 3000
}
```

## Vérification

Pour vérifier que la configuration fonctionne:

1. **Test de connexion:**
   - Le système tentera de se connecter au démarrage
   - Vérifiez les logs backend pour des erreurs

2. **Test d'upload:**
   - Upload une musique via l'interface
   - Vérifiez qu'elle apparaît dans votre Space

3. **Test de download:**
   - Le système télécharge automatiquement lors du traitement
   - Vérifiez les logs pour des erreurs

## Coûts DigitalOcean Spaces

- **$5/mois** pour 250GB de stockage
- **Gratuit** avec vos $200 de crédits pendant 1 an
- Assez pour des milliers de vidéos

## Migration depuis AWS S3

Si vous utilisez déjà AWS S3 et voulez migrer:

1. Créez un nouveau Space sur DigitalOcean
2. Mettez à jour les variables d'environnement
3. Redémarrez le backend
4. Les nouvelles vidéos utiliseront Spaces
5. Les anciennes vidéos restent sur S3 (ou migrez-les manuellement)

## Support

Le système utilise `boto3` qui est compatible avec:
- AWS S3
- DigitalOcean Spaces
- Tout autre service S3-compatible

Il suffit de configurer l'endpoint URL correctement.
