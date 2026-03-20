from django.urls import path
from .views import ArticlesIndexView

app_name = 'articles'

urlpatterns = [
    path('', ArticlesIndexView.as_view(), name='index'),
]
