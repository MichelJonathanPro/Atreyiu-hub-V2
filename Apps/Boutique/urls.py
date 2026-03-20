from django.urls import path
from .views import BoutiqueIndexView

app_name = 'boutique'

urlpatterns = [
    path('', BoutiqueIndexView.as_view(), name='index'),
]
