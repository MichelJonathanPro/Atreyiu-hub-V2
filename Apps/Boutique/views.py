from django.views.generic import TemplateView

class BoutiqueIndexView(TemplateView):
    template_name = 'Boutique/Boutique_index.html'

class BoutiqueDetailView(TemplateView):
    template_name = 'Boutique/Boutique_detail.html'

class BoutiquePanierView(TemplateView):
    template_name = 'Boutique/Boutique_panier.html'

class BoutiquePaiementView(TemplateView):
    template_name = 'Boutique/Boutique_paiement.html'
