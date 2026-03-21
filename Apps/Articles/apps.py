import os
import threading
import time
from django.apps import AppConfig

class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Apps.Articles'

    def ready(self):
        # Start background sync only if we are in the main process
        # and not in a management command (like migrate or sync_articles itself)
        if os.environ.get('RUN_MAIN') == 'true':
            threading.Thread(target=self.start_sync_loop, daemon=True).start()

    def start_sync_loop(self):
        from django.core.management import call_command
        # Wait a bit for the server to start properly
        time.sleep(15) 
        while True:
            try:
                # We don't use --watch here, just one sync pass
                call_command('sync_articles')
            except Exception:
                # Silent fail for the background task to avoid crashing server
                pass
            
            # Wait 5 minutes before next sync
            time.sleep(300)
