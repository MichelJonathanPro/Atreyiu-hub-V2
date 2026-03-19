from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse

def index(request):
    return render(request, 'homepage/index.html')

def devtools_json(request):
    return JsonResponse({}, status=200)

def error_404(request, exception):
    return render(request, '404/404-error.html', status=404)

def contact(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        subject_key = request.POST.get('subject', '')
        message_content = request.POST.get('message', '')
        
        # Determine sender info
        if request.user.is_authenticated:
            sender_name = f"{request.user.username} (Identifié)"
            sender_email = request.user.email
        else:
            sender_name = f"{first_name} {last_name} (Non identifié)"
            sender_email = email
            
        # Map subject key to readable text
        subjects = {
            'bug': 'Signaler un bug',
            'feedback': 'Félicitations, le site est top !',
            'display': "Dysfonctionnements d'affichage sur le site",
            'feature': 'Suggestion de fonctionnalité',
            'general': 'Question générale',
            'other': 'Autre',
        }
        subject_text = subjects.get(subject_key, 'Contact sans sujet')
        
        # Compose email
        full_subject = f"[Atreyiu-Hub Contact] {subject_text}"
        
        # HTML Content
        html_content = render_to_string('emails/contact_notification.html', {
            'sender_name': sender_name,
            'sender_email': sender_email,
            'subject_text': subject_text,
            'message_content': message_content,
        })
        
        try:
            email = EmailMessage(
                full_subject,
                html_content,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
            )
            email.content_subtype = "html"  # Main content is now text/html
            email.send(fail_silently=False)
            messages.success(request, "Votre message a été envoyé avec succès !")
        except Exception as e:
            messages.error(request, "Une erreur est survenue lors de l'envoi du message. Veuillez réessayer plus tard.")
            
        return redirect('homepage:contact')
        
    return render(request, 'Contact/Contact.html')

from .utils import get_website_updates

def website_updates(request):
    updates = get_website_updates()
    return render(request, 'Website_Updates/Website_Updates.html', {'updates': updates})
