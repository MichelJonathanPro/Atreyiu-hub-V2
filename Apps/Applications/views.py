from django.views.generic import TemplateView

class ApplicationsIndexView(TemplateView):
    template_name = 'Applications/Applications.html'
