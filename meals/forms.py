from django import forms
from .models import DailyMeal

class DailyMealForm(forms.ModelForm):
    class Meta:
        model = DailyMeal
        fields = ['food', 'quantity', 'date']
