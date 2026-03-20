from django.urls import path
from .views import PortfoliosIndexView, PortfoliosDetailView

app_name = 'portfolios'

urlpatterns = [
    path('', PortfoliosIndexView.as_view(), name='index'),
    path('detail/', PortfoliosDetailView.as_view(), name='detail'),
]

