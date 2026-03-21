from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Article
from .forms import ArticleForm

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class ArticlesIndexView(ListView):
    model = Article
    template_name = 'Articles/Articles_index.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        queryset = Article.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_published=True)
        
        # Filtering
        category = self.request.GET.get('category')
        tag = self.request.GET.get('tag')
        q = self.request.GET.get('q')
        
        if category:
            queryset = queryset.filter(category=category)
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        if q:
            queryset = queryset.filter(title__icontains=q) | queryset.filter(content__icontains=q)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all unique tags from articles
        all_tags = Article.objects.values_list('tags', flat=True)
        unique_tags = set()
        for tags_str in all_tags:
            if tags_str:
                for tag in tags_str.split(','):
                    unique_tags.add(tag.strip())
        context['available_tags'] = sorted(list(unique_tags))
        return context

class ArticlesDetailView(DetailView):
    model = Article
    template_name = 'Articles/Articles_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

class ArticleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'Articles/article_form.html'
    success_url = reverse_lazy('articles:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'Articles/article_form.html'
    
    def get_success_url(self):
        return reverse_lazy('articles:detail', kwargs={'slug': self.object.slug})

class ArticleDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Article
    template_name = 'Articles/article_confirm_delete.html'
    success_url = reverse_lazy('articles:index')

