from django.urls import path
from .views import TutorielsIndexView, TutorielsDetailView

app_name = 'tutoriels'

urlpatterns = [
    path('', TutorielsIndexView.as_view(), name='index'),
    path('detail/', TutorielsDetailView.as_view(), name='detail'),
]

