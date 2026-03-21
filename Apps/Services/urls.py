from django.urls import path
from .views import ServicesIndexView

app_name = 'services'

urlpatterns = [
    path('', ServicesIndexView.as_view(), name='index'),
]
