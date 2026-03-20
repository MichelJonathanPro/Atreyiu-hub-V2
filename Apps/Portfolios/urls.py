from django.urls import path
from .views import PortfoliosIndexView

app_name = 'portfolios'

urlpatterns = [
    path('', PortfoliosIndexView.as_view(), name='index'),
]
