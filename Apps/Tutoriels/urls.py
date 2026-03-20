from django.urls import path
from .views import TutorielsIndexView

app_name = 'tutoriels'

urlpatterns = [
    path('', TutorielsIndexView.as_view(), name='index'),
]
