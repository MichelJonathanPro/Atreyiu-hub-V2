from django.urls import path
from .views import BoutiqueIndexView, BoutiqueDetailView, BoutiquePanierView, BoutiquePaiementView

app_name = 'boutique'

urlpatterns = [
    path('', BoutiqueIndexView.as_view(), name='index'),
    path('detail/', BoutiqueDetailView.as_view(), name='detail'),
    path('panier/', BoutiquePanierView.as_view(), name='panier'),
    path('paiement/', BoutiquePaiementView.as_view(), name='paiement'),
]
