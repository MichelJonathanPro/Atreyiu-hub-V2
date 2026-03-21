from django.urls import path
from .views import (
    ArticlesIndexView, ArticlesDetailView, 
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView
)

app_name = 'articles'

urlpatterns = [
    path('', ArticlesIndexView.as_view(), name='index'),
    path('create/', ArticleCreateView.as_view(), name='create'),
    path('<slug:slug>/', ArticlesDetailView.as_view(), name='detail'),
    path('<slug:slug>/update/', ArticleUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', ArticleDeleteView.as_view(), name='delete'),
]

