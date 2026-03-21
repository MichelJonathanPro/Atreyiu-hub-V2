import os
import re
import requests
import frontmatter
import urllib3
from urllib.parse import quote
from django.core.management.base import BaseCommand
from django.conf import settings
from Apps.Articles.models import Article
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Disable SSL warnings for self-signed certificates used by Obsidian Local REST API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

User = get_user_model()

class Command(BaseCommand):
    help = 'Sync articles from Obsidian Local REST API with Wikilinks and Image support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Run in a loop to sync automatically every 5 minutes',
        )

    def handle(self, *args, **options):
        watch_mode = options.get('watch')
        
        if watch_mode:
            self.stdout.write(self.style.NOTICE("Mode automatique activé (surveillance toutes les 5 minutes)..."))
            import time
            while True:
                try:
                    self.sync_logic()
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Erreur durant la synchro auto : {e}"))
                
                self.stdout.write(self.style.NOTICE("Prochaine synchronisation dans 5 minutes... Appuyez sur Ctrl+C pour arrêter."))
                time.sleep(300)
        else:
            self.sync_logic()

    def sync_logic(self):
        api_url = os.getenv('OBSIDIAN_REST_API_URL', 'https://127.0.0.1:27124')
        api_token = os.getenv('OBSIDIAN_REST_API_TOKEN')
        
        if not api_token:
            self.stderr.write(self.style.ERROR('OBSIDIAN_REST_API_TOKEN not found in environment'))
            return

        headers = {
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/json'
        }

        # Specific target folder relative to vault root
        target_folder = 'Mes Websites/Atreyiu-Hub.com/Pages/Articles/'
        
        # List files in the folder (with URL encoding)
        quoted_target_folder = quote(target_folder, safe='/')
        try:
            response = requests.get(f"{api_url}/vault/{quoted_target_folder}", headers=headers, verify=False, timeout=10)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erreur de connexion à l'API Obsidian : {e}"))
            return

        if response.status_code != 200:
            self.stderr.write(self.style.ERROR(f"Impossible d'accéder au dossier {target_folder} (Code: {response.status_code})"))
            return
            
        data = response.json()
        files = data.get('files', [])
        md_files = [f for f in files if f.endswith('.md')]

        if not md_files:
            self.stdout.write(f"Aucune note Markdown trouvée dans {target_folder}")
            return

        author = User.objects.filter(is_staff=True).first()
        if not author:
            self.stderr.write(self.style.ERROR('Aucun utilisateur administrateur trouvé pour attribuer les articles'))
            return

        success_count = 0
        update_count = 0

        for file_name in md_files:
            full_file_path = f"{target_folder}{file_name}"
            
            try:
                quoted_full_path = quote(full_file_path, safe='/')
                file_response = requests.get(f"{api_url}/vault/{quoted_full_path}", headers=headers, verify=False, timeout=10)
                if file_response.status_code != 200:
                    self.stderr.write(self.style.WARNING(f"Échec de la récupération de {full_file_path}: {file_response.status_code}"))
                    continue
                
                post = frontmatter.loads(file_response.text)
                metadata = post.metadata
                content = post.content
                
                # Pre-process Obsidian content (Wikilinks and Images)
                content = self.process_obsidian_content(content, api_url, headers, target_folder)
                
                # Metadata extraction with French/English support
                title = metadata.get('Titre') or metadata.get('title') or file_name.replace('.md', '')
                category = metadata.get('Catégorie') or metadata.get('category') or 'Digital'
                
                tags = metadata.get('Tags') or metadata.get('tags') or ''
                if isinstance(tags, list):
                    tags = ', '.join(tags)
                
                is_published = metadata.get('Activer la publication')
                if is_published is None:
                    is_published = metadata.get('published', True)
                
                if isinstance(is_published, str):
                    is_published = is_published.lower() in ['true', 'yes', 'y', '1', 'vrai']
                
                nom_utilisateur = metadata.get('Nom Utilisateur') or metadata.get('author')
                author_obj = author 
                if nom_utilisateur:
                    user_match = User.objects.filter(username__iexact=nom_utilisateur).first()
                    if user_match:
                        author_obj = user_match
                
                # Thumbnail extraction from YAML (e.g., Thumbnail: [[image.png]])
                thumbnail_meta = metadata.get('Thumbnail') or metadata.get('thumbnail')
                image_url = None
                if thumbnail_meta:
                    # Clean Wikilink syntax [[ ]]
                    clean_thumb = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', r'\1', str(thumbnail_meta)).strip()
                    image_url = self.resolve_and_download_image(clean_thumb, api_url, headers, target_folder)
                
                article, created = Article.objects.update_or_create(
                    obsidian_path=full_file_path,
                    defaults={
                        'title': title,
                        'content': content,
                        'category': category,
                        'tags': tags,
                        'is_published': bool(is_published),
                        'author': author_obj
                    }
                )

                # Set the image field if found
                if image_url:
                    # image_url is like '/media/articles/attachments/image.png'
                    # We want to set the ImageField relative to MEDIA_ROOT
                    relative_path = image_url.replace(settings.MEDIA_URL, '')
                    article.image = relative_path
                    article.save()
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Article créé : {title}"))
                    success_count += 1
                else:
                    self.stdout.write(self.style.SUCCESS(f"Article mis à jour : {title}"))
                    update_count += 1
            except Exception as e:
                self.stderr.write(self.style.WARNING(f"Erreur lors du traitement de {full_file_path} : {e}"))

        self.stdout.write(self.style.SUCCESS(f"Synchronisation terminée. Créés : {success_count}, Mis à jour : {update_count}"))

    def process_obsidian_content(self, content, api_url, headers, target_folder):
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')

        # Simple replacement for all Wikilinks [[ ]] and embeds ![[ ]]
        def replace_obsidian_link(match):
            is_embed = match.group(0).startswith('!')
            target = match.group(1).strip()
            alias = match.group(2).strip() if match.group(2) else target
            
            # If it's an image file, we always embed it (as requested previously)
            if target.lower().endswith(image_extensions):
                local_url = self.resolve_and_download_image(target, api_url, headers, target_folder)
                if local_url:
                    # We use HTML <img> tag instead of Markdown to ensure it works even inside HTML blocks (like galleries)
                    return f'<img src="{local_url}" alt="{target}" class="img-fluid rounded">'
                return f"![[Image non trouvée : {target}]]"
            
            # Otherwise, it's a link to another article
            slug = slugify(target)
            return f"[{alias}](/articles/{slug}/)"

        # Process both ![[ ]] and [[ ]] with the same logic
        content = re.sub(r'!?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', replace_obsidian_link, content)
        
        return content

    def resolve_and_download_image(self, filename, api_url, headers, current_folder):
        # 1. Try common direct paths first (fast)
        parent_folder = '/'.join(current_folder.split('/')[:-3]) # 'Mes Websites/Atreyiu-Hub.com/'
        
        possible_paths = [
            f"{current_folder}{filename}",
            f"{current_folder}Attachments/{filename}",
            f"{current_folder}Médias/{filename}",
            f"{parent_folder}/Attachments/{filename}",
            f"{parent_folder}/Médias/{filename}",
            f"Médias/{filename}",
            filename
        ]
        
        for path in possible_paths:
            path = path.replace('//', '/')
            if self.try_download(path, filename, api_url, headers):
                return f"{settings.MEDIA_URL}articles/attachments/{filename}"

        # 2. Deep search in 'Médias/' if not found (slower)
        found_path = self.recursive_find(api_url, headers, "Médias/", filename)
        if found_path and self.try_download(found_path, filename, api_url, headers):
             return f"{settings.MEDIA_URL}articles/attachments/{filename}"
                
        return None

    def try_download(self, path, filename, api_url, headers):
        quoted_path = quote(path, safe='/')
        try:
            response = requests.get(f"{api_url}/vault/{quoted_path}", headers=headers, verify=False, timeout=5)
            if response.status_code == 200:
                media_subdir = 'articles/attachments'
                full_media_path = os.path.join(settings.MEDIA_ROOT, media_subdir, filename)
                os.makedirs(os.path.dirname(full_media_path), exist_ok=True)
                with open(full_media_path, 'wb') as f:
                    f.write(response.content)
                return True
        except:
            pass
        return False

    def recursive_find(self, api_url, headers, folder_path, filename, depth=0):
        if depth > 3: return None # Limit depth
        quoted_folder = quote(folder_path, safe='/')
        try:
            response = requests.get(f"{api_url}/vault/{quoted_folder}", headers=headers, verify=False, timeout=5)
            if response.status_code != 200: return None
            
            data = response.json()
            for f in data.get('files', []):
                full_path = f"{folder_path}{f}"
                if f.endswith('/'):
                    res = self.recursive_find(api_url, headers, full_path, filename, depth + 1)
                    if res: return res
                elif f.lower() == filename.lower():
                    return full_path
        except:
            pass
        return None
