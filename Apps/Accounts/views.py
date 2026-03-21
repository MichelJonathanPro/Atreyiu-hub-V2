from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from .tokens import account_activation_token
from .forms import SignupForm, EmailChangeForm, UserUpdateForm, ProfileUpdateForm
from .utils import send_activation_email

import time
from django.core.cache import cache

def signup_view(request):
    if request.method == 'POST':
        # Simple Rate Limiting by IP
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'signup_lock_{ip}'
        if cache.get(cache_key):
            messages.error(request, "Trop de tentatives. Veuillez patienter une minute.")
            return redirect('signup')
        
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            
            # Set lock for 60 seconds
            cache.set(cache_key, True, 60)
            
            if send_activation_email(request, user):
                messages.success(request, 'Un lien d\'activation a été envoyé à votre adresse e-mail.')
            else:
                messages.error(request, "Erreur : adresse e-mail non valide.")
            
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Félicitations ! Votre compte est maintenant activé.')
        return redirect('login')
    else:
        messages.error(request, 'Le lien d\'activation est invalide ou a expiré.')
        return redirect('signup')

def login_view(request):
    if request.method == 'POST':
        # Simple Rate Limiting by IP to prevent brute force
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'login_lock_{ip}'
        if cache.get(cache_key):
            messages.error(request, "Trop de tentatives de connexion. Veuillez patienter une minute.")
            return redirect('login')

        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active:
                login(request, user)
                
                # Handle "Remember Me"
                if request.POST.get('remember_me'):
                    # Session expires in 2 weeks (set in settings.SESSION_COOKIE_AGE)
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                else:
                    # Session expires when browser closes
                    request.session.set_expiry(0)
                
                # Clear lock on successful login
                cache.delete(cache_key)
                return redirect('homepage:index')
            else:
                messages.error(request, 'Veuillez activer votre compte via l\'e-mail envoyé.')
        else:
            # Set lock on failed attempt (or increment a counter, but here we stay simple)
            cache.set(cache_key, True, 60)
            
            # Check if user exists but is inactive
            username = request.POST.get('username')
            user = User.objects.filter(username=username).first()
            if user and not user.is_active:
                messages.error(request, 'Votre compte n\'est pas encore activé.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')

from django.contrib.auth.decorators import login_required

@login_required
def account_home(request):
    return render(request, 'accounts/account-home.html')

@login_required
def account_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('account_profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/account-profile.html', context)

@login_required
def account_security(request):
    if request.method == 'POST':
        if 'change_email' in request.POST:
            email_form = EmailChangeForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Votre adresse e-mail a été mise à jour.')
                return redirect('account_security')
            else:
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire d\'e-mail.')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Crucial pour ne pas déconnecter l'utilisateur
                messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
                return redirect('account_security')
            else:
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire de mot de passe.')
        
        elif 'delete_account' in request.POST:
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Votre compte a été supprimé définitivement.')
            return redirect('homepage:index')
            
    email_form = EmailChangeForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    
    context = {
        'email_form': email_form,
        'password_form': password_form,
    }
    return render(request, 'accounts/account-security.html', context)

@login_required
def account_billing(request):
    return render(request, 'accounts/account-billing.html')

@login_required
def account_team(request):
    return render(request, 'accounts/account-team.html')

@login_required
def account_notification(request):
    return render(request, 'accounts/account-notification.html')

@login_required
def account_app_integration(request):
    return render(request, 'accounts/account-app-integration.html')

@login_required
def account_device_session(request):
    from .models import UserSession
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    if request.method == 'POST' and 'revoke_session' in request.POST:
        session_key_to_revoke = request.POST.get('revoke_session')
        user_session = UserSession.objects.filter(session_key=session_key_to_revoke, user=request.user).first()
        if user_session:
            Session.objects.filter(session_key=session_key_to_revoke).delete()
            user_session.delete()
            messages.success(request, "Session révoquée avec succès.")
            return redirect('account_device_session')

    # Cleanup expired sessions for this user
    valid_sessions = Session.objects.filter(expire_date__gte=timezone.now()).values_list('session_key', flat=True)
    UserSession.objects.filter(user=request.user).exclude(session_key__in=valid_sessions).delete()

    current_session_key = request.session.session_key
    all_sessions = UserSession.objects.filter(user=request.user).order_by('-last_activity')
    
    web_sessions = [s for s in all_sessions if not s.is_mobile]
    mobile_sessions = [s for s in all_sessions if s.is_mobile]
    
    context = {
        'web_sessions': web_sessions,
        'mobile_sessions': mobile_sessions,
        'current_session_key': current_session_key
    }
    
    return render(request, 'accounts/account-device-session.html', context)

@login_required
def account_social_links(request):
    return render(request, 'accounts/account-social-links.html')

@login_required
def account_appearance(request):
    return render(request, 'accounts/account-appearance.html')
