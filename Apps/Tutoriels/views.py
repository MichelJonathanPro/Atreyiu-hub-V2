from django.views.generic import TemplateView

class TutorielsIndexView(TemplateView):
    template_name = 'Tutoriels/Tutoriels_index.html'

class TutorielsDetailView(TemplateView):
    template_name = 'Tutoriels/Tutoriels_detail.html'

