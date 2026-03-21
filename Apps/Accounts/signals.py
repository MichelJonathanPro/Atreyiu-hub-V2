import os
import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def export_user_to_obsidian(sender, instance, created, **kwargs):
    _sync_user_to_obsidian(instance, status_override=None)

@receiver(post_delete, sender=User)
def mark_user_deleted_in_obsidian(sender, instance, **kwargs):
    _sync_user_to_obsidian(instance, status_override="Supprimé")

def _sync_user_to_obsidian(instance, status_override=None):
    api_url = getattr(settings, 'OBSIDIAN_REST_API_URL', 'http://127.0.0.1:27124')
    api_token = getattr(settings, 'OBSIDIAN_REST_API_TOKEN', None)
    vault_path = getattr(settings, 'OBSIDIAN_VAULT_PATH', None)
    
    # Prepare user information
    username = instance.username
    email = instance.email
    date_joined = instance.date_joined.strftime('%Y-%m-%d %H:%M:%S')
    last_login = instance.last_login.strftime('%Y-%m-%d %H:%M:%S') if instance.last_login else "Jamais"
    
    if status_override:
        is_active = status_override
    else:
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


from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def create_or_update_user_session(sender, user, request, **kwargs):
    if not request:
        return
        
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
        
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')
        
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Basic parsing
    is_mobile = False
    if "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent:
        is_mobile = True
        
    if "Windows" in user_agent:
        os_name = "Windows"
    elif "Mac" in user_agent:
        os_name = "macOS"
    elif "Linux" in user_agent:
        os_name = "Linux"
    elif "Android" in user_agent:
        os_name = "Android"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        os_name = "iOS"
    else:
        os_name = "Inconnu"
        
    if "Edg" in user_agent:
        browser = "Edge"
    elif "Chrome" in user_agent:
        browser = "Chrome"
    elif "Firefox" in user_agent:
        browser = "Firefox"
    elif "Safari" in user_agent:
        browser = "Safari"
    else:
        browser = "Navigateur Web"
        
    device = f"{browser} sur {os_name}"
    
    from .models import UserSession
    UserSession.objects.update_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': ip_address,
            'device': device,
            'is_mobile': is_mobile,
            'last_activity': timezone.now()
        }
    )
