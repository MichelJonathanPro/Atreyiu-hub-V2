from django.urls import path
from . import views

app_name = 'website_updates'

urlpatterns = [
    path('', views.index, name='index'),
]
