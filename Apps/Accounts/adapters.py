from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
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

    def get_signup_redirect_url(self, request):
        """
        Redirect social signups to their own logic (which makes them inactive).
        After save_user, Allauth might try to redirect based on this.
        """
        return redirect('login')

class CustomAccountAdapter(DefaultAccountAdapter):
    def respond_user_inactive(self, request, user):
        """
        Redirect to login instead of the default inactive page.
        """
        messages.info(request, "Votre compte n'est pas encore activé. Veuillez vérifier vos e-mails.")
        return redirect('login')
