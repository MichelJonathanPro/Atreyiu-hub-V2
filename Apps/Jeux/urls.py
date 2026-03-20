from django.urls import path
from .views import JeuxIndexView, JeuxDetailView

app_name = 'jeux'

urlpatterns = [
    path('', JeuxIndexView.as_view(), name='index'),
    path('detail/', JeuxDetailView.as_view(), name='detail'),
]

