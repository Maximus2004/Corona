from django.urls import path
from . import views
from django.contrib.auth import views as v

urlpatterns = [
    path('', views.main, name='main'),
    # path('results/', views.results, name='results'),
]