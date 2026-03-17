from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from .utils import send_activation_email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In our case, we want to
        enforce email validation by setting the user as inactive.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Enforce inactivity for email validation
        user.is_active = False
        user.save()
        
        # Send our custom activation email
        try:
            send_activation_email(request, user)
            messages.success(request, 'Votre compte a été créé. Un lien d\'activation a été envoyé par e-mail.')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'e-mail d'activation : {str(e)}")
            
        return user
