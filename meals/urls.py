from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_meal, name='add_meal'),
    path('new_item/', views.add_food, name='add_food'),
    path('history/', views.history, name='history'),
    path('food-autocomplete/', views.food_autocomplete, name='food_autocomplete'),

]
