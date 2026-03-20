from django.urls import path
from .views import ArticlesIndexView, ArticlesDetailView

app_name = 'articles'

urlpatterns = [
    path('', ArticlesIndexView.as_view(), name='index'),
    path('detail/', ArticlesDetailView.as_view(), name='detail'),
]

