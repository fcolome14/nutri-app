from django.shortcuts import render, redirect
from .models import DailyMeal, Food
from django.http import JsonResponse
from .forms import FoodForm
import json
from django.contrib.auth.decorators import login_required
import plotly.graph_objs as go
from plotly.offline import plot
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date

macro_colors = {
    'Protein': '#636EFA',  # blue
    'Carbs':   '#EF553B',  # red
    'Fats':    '#00CC96'   # green
}

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


def _check_date(start_date, end_date):
    if isinstance(start_date, str) and start_date:
        start_date = parse_date(start_date)
    else:
        start_date = datetime.today().date() - timedelta(days=6)

    if isinstance(end_date, str) and end_date:
        end_date = parse_date(end_date)
    else:
        end_date = datetime.today().date()

    return start_date, end_date

def get_calorie_extremes(day_stats):
    if day_stats:
        max_day = max(day_stats, key=lambda d: day_stats[d]['calories'])
        min_day = min(day_stats, key=lambda d: day_stats[d]['calories'])
        return {
            'max_calories_day': max_day,
            'max_calories_value': day_stats[max_day]['calories'],
            'min_calories_day': min_day,
            'min_calories_value': day_stats[min_day]['calories'],
        }
    return {
        'max_calories_day': None,
        'max_calories_value': None,
        'min_calories_day': None,
        'min_calories_value': None,
    }

def history(request):
    # Default range: past 7 days

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date') or datetime.today().date()
    start_date_dt, end_date_dt = _check_date(start_date, end_date)
    
    days = (end_date_dt - start_date_dt).days + 1

    if start_date_dt:
        meals = DailyMeal.objects.filter(
            user=get_dummy_user(),
            date__range=[start_date_dt, end_date_dt]
        ).order_by('date')
    else:
        meals = DailyMeal.objects.filter(user=get_dummy_user()).order_by('date')
    
    day_stats = {}
    if meals.exists() and days>0:
        for meal in meals:
            day = meal.date
            if day not in day_stats:
                day_stats[day] = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}
            day_stats[day]['calories'] += meal.calories or 0
            day_stats[day]['protein'] += meal.protein or 0
            day_stats[day]['carbs'] += meal.carbs or 0
            day_stats[day]['fats'] += meal.fats or 0

        # Extract stats
        dates = sorted(day_stats.keys())
        calories = [day_stats[d]['calories'] for d in dates]
        protein = [day_stats[d]['protein'] for d in dates]
        carbs = [day_stats[d]['carbs'] for d in dates]
        fats = [day_stats[d]['fats'] for d in dates]
        
        # Extract max/min calories days
        cal_ranges = get_calorie_extremes(day_stats)
        max_calories_day = cal_ranges['max_calories_day']
        max_calories_value = cal_ranges['max_calories_value']
        min_calories_day = cal_ranges['min_calories_day']
        min_calories_value = cal_ranges['min_calories_value']
    else:
        # Empty result defaults
        dates = []
        calories = []
        protein = []
        carbs = []
        fats = []
        max_calories_value = min_calories_value = 0
        max_calories_day = min_calories_day = None

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
               hole=0.3,
               marker=dict(colors=[
                macro_colors['Protein'],
                macro_colors['Carbs'],
                macro_colors['Fats']
               ]),)
    ])
    pie_chart = plot(fig2, output_type='div', include_plotlyjs=False)

    # Bar Chart – Macros per Day
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=dates, y=protein, name='Protein',
                        marker=dict(color=macro_colors['Protein'])))
    fig3.add_trace(go.Bar(x=dates, y=carbs, name='Carbs',
                        marker=dict(color=macro_colors['Carbs'])))
    fig3.add_trace(go.Bar(x=dates, y=fats, name='Fats',
                        marker=dict(color=macro_colors['Fats'])))
    fig3.update_layout(barmode='group', title='Macros per Day')
    bar_chart = plot(fig3, output_type='div', include_plotlyjs=False)

    return render(request, 'history/history.html', {
        'line_plot': line_plot,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
        'summary': {
            'calories': round(sum(calories)/days,2),
            'protein': round(total_protein/days,2),
            'carbs': round(total_carbs/days,2),
            'fats': round(total_fats/days,2),
        },
        'cal_ranges':{
            'max_calories_day': max_calories_day,
            'max_calories_value': max_calories_value,
            'min_calories_day': min_calories_day,
            'min_calories_value': min_calories_value,
        },
        'days': days,
        'start_date': start_date_dt.isoformat(),
        'end_date': end_date_dt.isoformat(),
    })

