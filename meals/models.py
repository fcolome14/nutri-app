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
    serving_amount = models.FloatField(blank=True, null=True)  # New field for serving amount
    UNIT_CHOICES = [
        ('g', 'Grams'),
        ('ml', 'Milliliters'),
        ('units', 'Units'),
    ]
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='g')  # Restricted unit choices
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.brand or 'Unknown Brand'} - {self.product or 'Unknown Product'}"

class DailyMeal(models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)  # Replace with UUID
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.FloatField()
    date = models.DateField()
    carbs = models.FloatField(blank=True, null=True)
    fats = models.FloatField(blank=True, null=True)
    fiber = models.FloatField(blank=True, null=True)
    protein = models.FloatField(blank=True, null=True)
    calories = models.FloatField(blank=True, null=True)

class BMRRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    age = models.PositiveIntegerField()
    height = models.FloatField()  # Height in cm
    weight = models.FloatField()  # Weight in kg
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')])
    activity_level = models.CharField(max_length=20, choices=[
        ('sedentary', 'Sedentary'),
        ('light', 'Lightly active'),
        ('moderate', 'Moderately active'),
        ('active', 'Active'),
        ('very-active', 'Very active'),
    ])
    bmr = models.FloatField()  # Computed BMR value
    date = models.DateField(auto_now_add=True)  # Date of the record

    def __str__(self):
        return f"{self.user.username} - BMR: {self.bmr} kcal/day on {self.date}"