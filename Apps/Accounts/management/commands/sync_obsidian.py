import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Apps.Accounts.signals import export_user_to_obsidian

class Command(BaseCommand):
    help = 'Synchronise tous les utilisateurs existants vers le vault Obsidian'

    def handle(self, *args, **options):
        users = User.objects.all()
        count = 0
        for user in users:
            # Re-trigger the signal logic manually for each user
            export_user_to_obsidian(sender=User, instance=user, created=False)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Synchronisation terminée : {count} utilisateurs exportés.'))
