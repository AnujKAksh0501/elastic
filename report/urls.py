from django.urls import path, include
from . import views

urlpatterns = [
    path('work/matomo/visit-countries-list', views.AdminMatomoVisitCountriesList, name='AdminMatomoVisitCountriesList'),
    
]