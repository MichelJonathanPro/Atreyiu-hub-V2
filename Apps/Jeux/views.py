from django.views.generic import TemplateView

class JeuxIndexView(TemplateView):
    template_name = 'Jeux/Jeux_index.html'

class JeuxDetailView(TemplateView):
    template_name = 'Jeux/Jeux_detail.html'

