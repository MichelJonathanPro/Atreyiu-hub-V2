from django.views.generic import TemplateView

class ArticlesIndexView(TemplateView):
    template_name = 'Articles/Articles.html'
