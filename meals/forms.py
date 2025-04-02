from django import forms
from .models import DailyMeal, Food

class DailyMealForm(forms.ModelForm):
    class Meta:
        model = DailyMeal
        fields = ['quantity', 'date']

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['brand', 'product', 'calories', 'protein', 'carbs', 'fats', 'fiber', 'unit']
