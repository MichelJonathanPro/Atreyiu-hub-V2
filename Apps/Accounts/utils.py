from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token

def send_activation_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activez votre compte Atreyiu Hub'
    message = render_to_string('emails/activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    if to_email:
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = 'html'
        email.send(fail_silently=False)
        return True
    return False
