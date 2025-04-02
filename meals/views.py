from django.shortcuts import render, redirect
from .models import DailyMeal, Food
from django.http import JsonResponse
from .forms import FoodForm
import json
from django.contrib.auth.decorators import login_required
import plotly.graph_objs as go
from plotly.offline import plot

def home(request):
    return render(request, 'meals/home.html')

#@login_required
def add_meal(request):
    if request.method == 'POST':
        meals_data = json.loads(request.POST.get('meals_json', '[]'))
        for item in meals_data:
            try:
                food = Food.objects.get(id=item['food_id'])
                DailyMeal.objects.create(
                    user=request.user,
                    food=food,
                    quantity=item['quantity'],
                    date=item['date']
                )
            except Food.DoesNotExist:
                continue  # Or log
        return redirect('history')  # or your target view

    return render(request, 'meals/add_meal.html')


def food_autocomplete(request):
    query = request.GET.get('q', '')

    if not query:
        return JsonResponse([], safe=False)

    foods = Food.objects.filter(product__icontains=query)[:10]
    results = []

    for f in foods:
        product = f.product or "Unnamed"
        brand = f.brand or ""
        if brand.upper() == "NA":
            label = product
        else:
            label = f"{product} ({brand})"
        results.append({'id': f.id, 'name': label})

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

