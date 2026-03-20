from django.views.generic import TemplateView

class ArticlesIndexView(TemplateView):
    template_name = 'Articles/Articles_index.html'

class ArticlesDetailView(TemplateView):
    template_name = 'Articles/Articles_detail.html'

