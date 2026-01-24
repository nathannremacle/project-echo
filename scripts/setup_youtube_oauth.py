#!/usr/bin/env python3
"""
Script pour obtenir un refresh token OAuth 2.0 pour YouTube API
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes nécessaires pour YouTube API
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
]


def get_refresh_token(credentials_file: str, output_file: str = None):
    """
    Obtient un refresh token OAuth 2.0
    
    Args:
        credentials_file: Chemin vers le fichier credentials.json de Google Cloud
        output_file: Fichier de sortie pour sauvegarder les tokens (optionnel)
    """
    creds = None
    creds_dir = os.path.dirname(os.path.abspath(credentials_file))
    token_path = os.path.join(creds_dir, 'token.json')
    
    # Vérifier si on a déjà des tokens sauvegardés (à côté de credentials.json)
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Charger client_id et client_secret depuis credentials.json (fallback)
    with open(credentials_file, 'r') as f:
        client_config = json.load(f)
    # Support "installed" (Desktop app) ou "web"
    secrets = client_config.get('installed') or client_config.get('web') or {}
    fallback_client_id = secrets.get('client_id', '')
    fallback_client_secret = secrets.get('client_secret', '')
    
    # Si pas de credentials valides, demander l'autorisation
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            print("\n" + "="*60)
            print("  OUVRIR L'URL DANS VOTRE NAVIGATEUR")
            print("  (Si le navigateur ne s'ouvre pas, l'URL s'affiche ci-dessous.")
            print("  Copiez-collez-la dans Chrome, Firefox ou Edge.)")
            print("="*60 + "\n")
            # open_browser=False : l'URL est affichée dans le terminal pour copier-coller
            # (évite les problèmes quand webbrowser.open() ne fonctionne pas)
            creds = flow.run_local_server(
                port=0,
                open_browser=False,
                authorization_prompt_message=(
                    "Ouvrez cette URL dans votre navigateur :\n\n{url}\n\n"
                    "Après autorisation, vous serez redirigé vers localhost (la page peut indiquer une erreur, c'est normal).\n"
                ),
                success_message="Autorisation réussie. Vous pouvez fermer cet onglet et revenir au terminal.",
            )
        
        # Sauvegarder les credentials (token.json à côté de credentials.json)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    # Récupérer client_id, client_secret (creds ne les a pas toujours)
    client_id = getattr(creds, 'client_id', None) or fallback_client_id
    client_secret = getattr(creds, 'client_secret', None) or fallback_client_secret
    refresh_token = creds.refresh_token
    
    # Afficher les informations
    print("\n" + "="*60)
    print("CREDENTIALS OBTENUS")
    print("="*60)
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret}")
    print(f"Refresh Token: {refresh_token}")
    print("="*60)
    
    # Sauvegarder dans un fichier si demandé
    if output_file:
        output_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n✅ Credentials sauvegardés dans: {output_file}")
    
    print("\n📝 Utilisez ces valeurs dans votre configuration:")
    print("   - Client ID: Pour YOUTUBE_CLIENT_ID")
    print("   - Client Secret: Pour YOUTUBE_CLIENT_SECRET")
    print("   - Refresh Token: Pour YOUTUBE_REFRESH_TOKEN")
    print("\n⚠️  IMPORTANT: Gardez ces informations SECRÈTES!")
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python setup_youtube_oauth.py <credentials.json> [output.json]")
        print("\nÉtapes:")
        print("1. Allez sur https://console.cloud.google.com/")
        print("2. Créez un projet et activez YouTube Data API v3")
        print("3. Créez des OAuth 2.0 credentials (Desktop app)")
        print("4. Téléchargez le fichier JSON")
        print("5. Exécutez ce script avec le fichier JSON")
        sys.exit(1)
    
    credentials_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(credentials_file):
        print(f"❌ Fichier non trouvé: {credentials_file}")
        sys.exit(1)
    
    get_refresh_token(credentials_file, output_file)
