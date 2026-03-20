from django.urls import path
from .views import JeuxIndexView

app_name = 'jeux'

urlpatterns = [
    path('', JeuxIndexView.as_view(), name='index'),
]
