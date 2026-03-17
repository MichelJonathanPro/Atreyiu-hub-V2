from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from .tokens import account_activation_token
from .forms import SignupForm

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
            
            current_site = get_current_site(request)
            mail_subject = 'Activez votre compte Atreyiu Hub'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            if to_email:
                try:
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.content_subtype = 'html'  # Enable HTML rendering
                    email.send(fail_silently=False)
                    messages.success(request, 'Un lien d\'activation a été envoyé à votre adresse e-mail.')
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")
                    # Optionally delete user or keep it as inactive for periodic cleanup
            
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
