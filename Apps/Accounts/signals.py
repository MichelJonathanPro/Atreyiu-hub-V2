import os
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

@receiver(post_save, sender=User)
def export_user_to_obsidian(sender, instance, created, **kwargs):
    api_url = getattr(settings, 'OBSIDIAN_REST_API_URL', 'http://127.0.0.1:27124')
    api_token = getattr(settings, 'OBSIDIAN_REST_API_TOKEN', None)
    vault_path = getattr(settings, 'OBSIDIAN_VAULT_PATH', None)
    
    # Prepare user information
    username = instance.username
    email = instance.email
    date_joined = instance.date_joined.strftime('%Y-%m-%d %H:%M:%S')
    last_login = instance.last_login.strftime('%Y-%m-%d %H:%M:%S') if instance.last_login else "Jamais"
    is_active = "Actif" if instance.is_active else "En attente d'activation"
    is_staff = "Admin" if instance.is_staff else "Utilisateur"
    sync_date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    # Markdown Content
    content = f"""---
type: utilisateur
username: {username}
email: {email}
date_joined: {date_joined}
status: {is_active}
role: {is_staff}
last_sync: {sync_date}
---

# Fiche Utilisateur : {username}

## Informations de Compte
- **Email :** {email}
- **Date d'inscription :** {date_joined}
- **Dernière connexion :** {last_login}
- **Statut :** {is_active}
- **Rôle :** {is_staff}

## Informations Légales & Analyse
- **ID Base de données :** {instance.pk}
- **Consentement RGPD :** Accepté (Inscrit via formulaire sécurisé)
- **Source :** Atreyiu Hub V2
- **Dernière Synchronisation :** {sync_date}

---
*Note générée automatiquement par le système d'authentification Atreyiu Hub.*
"""

    filename = f"User_{username}.md"

    # Strategy 1: Attempt to use Obsidian REST API
    if api_token:
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # The Local REST API endpoint for files is usually /vault/path/to/file.md
            rel_path = ""
            if vault_path and "Obsidian Vault/" in vault_path:
                rel_path = vault_path.split("Obsidian Vault/")[1]
            
            target_path = os.path.join(rel_path, filename)
            url = f"{api_url.rstrip('/')}/vault/{target_path}"
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "text/markdown"
            }
            
            response = requests.put(url, data=content.encode('utf-8'), headers=headers, timeout=5, verify=False)
            if response.status_code in [200, 204]:
                return # Success!
        except Exception as e:
            print(f"Obsidian API failed, falling back to file system: {e}")

    # Strategy 2: Fallback to File System (especially for Prod or if API is down)
    if vault_path:
        if not os.path.exists(vault_path):
            try:
                os.makedirs(vault_path, exist_ok=True)
            except Exception:
                return

        file_path = os.path.join(vault_path, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error exporting to Obsidian file system: {e}")
