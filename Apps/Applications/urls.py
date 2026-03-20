from django.urls import path
from .views import ApplicationsIndexView

app_name = 'applications'

urlpatterns = [
    path('', ApplicationsIndexView.as_view(), name='index'),
]
