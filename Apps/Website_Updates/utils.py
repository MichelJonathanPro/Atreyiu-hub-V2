import os
import re
from django.conf import settings

def get_website_updates():
    """
    Lit et parse les fichiers Markdown du vault Obsidian pour les afficher sur le site.
    """
    history_path = getattr(settings, 'OBSIDIAN_HISTORY_PATH', None)
    if not history_path or not os.path.exists(history_path):
        return []

    updates = []
    
    # Liste tous les fichiers .md et les trie par numéro (décroissant)
    files = [f for f in os.listdir(history_path) if f.endswith('.md')]
    # Tri numérique basé sur le début du nom de fichier (ex: 20.nom.md)
    files.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else 0, reverse=True)

    for filename in files:
        file_path = os.path.join(history_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Nettoyage des caractères d'échappement si présents (certains hooks curl envoient des \n littéraux)
            content = content.replace('\\n', '\n')

            # Extraction du numéro de push et du message via regex
            # Format attendu: # Push n°X : Message
            header_match = re.search(r'# Push n°(\d+) : (.*)', content)
            push_number = header_match.group(1) if header_match else filename.split('.')[0]
            title = header_match.group(2).split('\n')[0].strip() if header_match else "Mise à jour sans titre"

            # Extraction de la date
            # Format attendu: - **Date** : YYYY-MM-DD HH:MM
            date_match = re.search(r'- \*\*Date\*\* : (.*)', content)
            raw_date = date_match.group(1).split('\n')[0].strip() if date_match else "Date inconnue"
            
            # Nettoyage final de la date (on retire tout ce qui suit si la regex a trop pris)
            display_date = raw_date

            # Extraction des statistiques (tout ce qui est après ---)
            parts = content.split('---')
            stats = ""
            if len(parts) > 1:
                # On prend la dernière partie qui contient généralement le git log -1 --stat
                stats = parts[-1].strip()

            # Détermination automatique du badge (simpliste pour l'instant)
            badge = "cleanup" # Default
            lower_title = title.lower()
            if any(word in lower_title for word in ['nouveau', 'ajout', 'initial', 'création', 'homepage']):
                badge = "new"
            elif any(word in lower_title for word in ['fix', 'correction', 'problème', 'bug', 'erreur']):
                badge = "fix"
            elif any(word in lower_title for word in ['sécurité', 'env', 'secret', 'sécure']):
                badge = "security"
            elif any(word in lower_title for word in ['nettoyage', 'suppression', 'retrait', 'cleanup']):
                badge = "cleanup"

            updates.append({
                'number': push_number,
                'title': title,
                'date': display_date
            })
        except Exception as e:
            print(f"Error parsing Obsidian file {filename}: {e}")
            continue

    return updates
