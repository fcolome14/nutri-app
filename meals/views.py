from django.shortcuts import render, redirect
from .models import DailyMeal, Food
from django.http import JsonResponse
from .forms import FoodForm
import json
from django.contrib.auth.decorators import login_required
import plotly.graph_objs as go
from plotly.offline import plot
from django.contrib.auth.models import User
from datetime import datetime

def home(request):
    return render(request, 'home/home.html')

#@login_required
def add_meal(request):
    if request.method == 'POST':
        meals_data = json.loads(request.POST.get('meals_json', '[]'))

        for item in meals_data:
            try:
                food = Food.objects.get(id=item['food_id'])
                quantity = float(item['quantity'])  # in grams/ml/units
                date = item['date']
            
                DailyMeal.objects.create(
                    user=get_dummy_user(),
                    food=food,
                    quantity=quantity,
                    date=date,
                    carbs=compute(food.carbs, quantity),
                    fats=compute(food.fats, quantity),
                    fiber=compute(food.fiber, quantity),
                    calories=compute(food.calories, quantity),
                    protein=compute(food.protein, quantity),
                )

            except (Food.DoesNotExist, KeyError, ValueError):
                continue  # log or skip silently

        return redirect('add_meal')

    return render(request, 'meals/add_meal.html')

def compute(value, quantity=100):
    return round((value or 0) / 100 * quantity, 2)

def get_dummy_user():
    return User.objects.get(username='usuario')

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
    return render(request, 'food/add_food.html', {'form': form})

def history(request):
    # Default range: past 7 days

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date') or datetime.today().date()

    if start_date:
        meals = DailyMeal.objects.filter(
            user=get_dummy_user(),
            date__range=[start_date, end_date]
        ).order_by('date')
    else:
        meals = DailyMeal.objects.filter(user=get_dummy_user()).order_by('date')

    # Group by date
    day_stats = {}
    for meal in meals:
        day = meal.date
        if day not in day_stats:
            day_stats[day] = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}
        day_stats[day]['calories'] += meal.calories or 0
        day_stats[day]['protein'] += meal.protein or 0
        day_stats[day]['carbs'] += meal.carbs or 0
        day_stats[day]['fats'] += meal.fats or 0

    dates = sorted(day_stats.keys())
    calories = [day_stats[d]['calories'] for d in dates]
    protein = [day_stats[d]['protein'] for d in dates]
    carbs = [day_stats[d]['carbs'] for d in dates]
    fats = [day_stats[d]['fats'] for d in dates]

    # Line Chart – Calories
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=dates, y=calories, mode='lines+markers', name='Calories'))
    line_plot = plot(fig1, output_type='div', include_plotlyjs=False)

    # Pie Chart – Macro Distribution
    total_protein = sum(protein)
    total_carbs = sum(carbs)
    total_fats = sum(fats)

    fig2 = go.Figure(data=[
        go.Pie(labels=['Protein', 'Carbs', 'Fats'],
               values=[total_protein, total_carbs, total_fats],
               hole=0.3)
    ])
    pie_chart = plot(fig2, output_type='div', include_plotlyjs=False)

    # Bar Chart – Macros per Day
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=dates, y=protein, name='Protein'))
    fig3.add_trace(go.Bar(x=dates, y=carbs, name='Carbs'))
    fig3.add_trace(go.Bar(x=dates, y=fats, name='Fats'))
    fig3.update_layout(barmode='group', title='Macros per Day')
    bar_chart = plot(fig3, output_type='div', include_plotlyjs=False)

    return render(request, 'history/history.html', {
        'line_plot': line_plot,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
        'summary': {
            'calories': round(sum(calories),2),
            'protein': round(total_protein,2),
            'carbs': round(total_carbs,2),
            'fats': round(total_fats,2),
        },
        'start_date': start_date,
        'end_date': end_date,
    })

