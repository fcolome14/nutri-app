from django.shortcuts import render, redirect
from .models import DailyMeal, Food
from django.http import JsonResponse
from .forms import DailyMealForm, FoodForm
from django.contrib.auth.decorators import login_required
import plotly.graph_objs as go
from plotly.offline import plot

def home(request):
    return render(request, 'meals/home.html')

#@login_required
def add_meal(request):
    if request.method == 'POST':
        form = DailyMealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            food_id = request.POST.get('food')
            if food_id:
                from .models import Food
                meal.food = Food.objects.get(id=food_id)
                meal.user = request.user
                meal.save()
                return redirect('history')
    else:
        form = DailyMealForm()
    return render(request, 'meals/add_meal.html', {'form': form})


def food_autocomplete(request):
    query = request.GET.get('q', '')
    foods = Food.objects.filter(product__icontains=query)[:10]
    results = [{'id': f.code, 'name': f.product} for f in foods]
    return JsonResponse(results, safe=False)

def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_food')
    else:
        form = FoodForm()
    return render(request, 'meals/add_food.html', {'form': form})

@login_required
def history(request):
    meals = DailyMeal.objects.filter(user=request.user).order_by('date')
    dates = [m.date for m in meals]
    calories = [m.get_total_calories() for m in meals]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=calories, mode='lines+markers', name='Calories'))
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render(request, 'meals/history.html', {'plot_div': plot_div})

