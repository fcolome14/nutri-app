from django import forms
from .models import DailyMeal, Food

class DailyMealForm(forms.ModelForm):
    class Meta:
        model = DailyMeal
        fields = ['quantity', 'date']

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(FoodForm, self).__init__(*args, **kwargs)
        self.fields['serving_amount'].initial = 100
