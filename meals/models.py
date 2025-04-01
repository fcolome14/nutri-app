from django.db import models
from django.contrib.auth.models import User
import uuid

class Food(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
    calories = models.FloatField(blank=True, null=True)
    protein = models.FloatField(blank=True, null=True)
    carbs = models.FloatField(blank=True, null=True)
    fats = models.FloatField(blank=True, null=True)
    fiber = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)  # grams, pieces, etc.
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.brand or 'Unknown Brand'} - {self.product or 'Unknown Product'}"

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

