from django.urls import path
from . import views

app_name = 'homepage'

urlpatterns = [
    path('', views.index, name='index'),
    path('.well-known/appspecific/com.chrome.devtools.json', views.devtools_json, name='devtools_json'),
    path('404-test/', views.error_404, {'exception': Exception()}, name='404_test'),
    path('contact/', views.contact, name='contact'),
    path('updates/', views.website_updates, name='website_updates'),
]
