from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_meal, name='add_meal'),
    path('history/', views.history, name='history'),
]
