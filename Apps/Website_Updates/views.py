from django.shortcuts import render
from .utils import get_website_updates

def index(request):
    updates = get_website_updates()
    return render(request, 'Website_Updates/Website_Updates.html', {'updates': updates})
