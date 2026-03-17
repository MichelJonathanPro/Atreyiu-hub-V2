from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Apps.Accounts'

    def ready(self):
        import Apps.Accounts.signals
