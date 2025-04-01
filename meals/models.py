from django.db import models
from django.contrib.auth.models import User

class Food(models.Model):
    name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    fiber = models.FloatField()
    unit = models.CharField(max_length=20)  # grams, pieces, etc.

    def __str__(self):
        return self.name

class DailyMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.FloatField()
    date = models.DateField()

    def get_total_calories(self):
        return self.quantity * self.food.calories

    def get_macros(self):
        return {
            'protein': self.quantity * self.food.protein,
            'carbs': self.quantity * self.food.carbs,
            'fats': self.quantity * self.food.fats,
            'fiber': self.quantity * self.food.fiber,
        }

