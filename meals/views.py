from django.shortcuts import render, redirect
from .models import DailyMeal, Food, BMRRecord
from django.http import JsonResponse
from .forms import FoodForm
import json
from django.contrib.auth.decorators import login_required
import plotly.graph_objs as go
from plotly.offline import plot
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.core.cache import cache

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
                continue 

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
    
    # Check if the query is in the cache
    cached_results = cache.get(f'food_autocomplete_{query}')
    if cached_results:
        return JsonResponse(cached_results, safe=False)
    
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

def bmr_weight(request):
    return render(request, 'bmr_weight/bmr_weight.html')

def compute_bmr(request):
    if request.method == 'POST':
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            formula = data.get('formula')
            age = int(data.get('age'))
            height = float(data.get('height'))
            weight = float(data.get('weight'))
            activity_level = data.get('activity_level')
            gender = data.get('gender')
            fat = data.get('fat')  # Optional

            if not formula or not age or not height or not weight or not activity_level or not gender:
                return JsonResponse({'error': 'All fields are required except Body Fat for non-Katch-McArdle formulas.'}, status=400)

            # Calculate BMR
            bmr = None
            if formula == 'mifflin-st-jeor':
                bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == 'male' else -161)
            elif formula == 'harris-benedict':
                if gender == 'male':
                    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
                else:
                    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            elif formula == 'katch-mcardle':
                if fat is None:
                    return JsonResponse({'error': 'Body Fat percentage is required for the Katch-McArdle formula.'}, status=400)
                fat = float(fat)
                if fat <= 0 or fat > 100:
                    return JsonResponse({'error': 'Body Fat percentage must be between 0 and 100.'}, status=400)
                lean_body_mass = weight * (1 - fat / 100)
                bmr = 370 + (21.6 * lean_body_mass)
            else:
                return JsonResponse({'error': 'Invalid formula selected.'}, status=400)

            # Adjust based on activity
            activity_multiplier = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'active': 1.725,
                'very-active': 1.9,
            }

            multiplier = activity_multiplier.get(activity_level)
            if not multiplier:
                return JsonResponse({'error': 'Invalid activity level selected.'}, status=400)

            adjusted_bmr = bmr * multiplier

            return JsonResponse({
                'bmr': round(bmr, 2),
                'bmr_adj': round(adjusted_bmr, 2)
            })

        except (ValueError, TypeError, KeyError) as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)

    return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)

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
    
    days = (end_date_dt - start_date_dt).days

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
        
        count_valid_days = 0
        for day in day_stats:
            if day_stats[day]['calories'] > 0:
                count_valid_days += 1
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
        count_valid_days = 1

    # Line Chart – Calories
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=dates, 
        y=calories, 
        mode='lines+markers', 
        name='Calories',
        hovertemplate='<b>Date:</b> %{x}<br><b>Calories:</b> %{y} kcal<extra></extra>'))
    fig1.update_layout(
        title='Calories Over Time',         # Chart title
        xaxis_title='Day',                 # X-axis title
        yaxis_title='Calories (kcal)',      # Y-axis title
    )
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
               ]),
               hovertemplate=(
                '<b>%{label}:</b> %{value} g<br>'
                '<b>Percentage:</b> %{percent}<extra></extra>'
                ),  
               )
    ])
    pie_chart = plot(fig2, output_type='div', include_plotlyjs=False)

    # Bar Chart – Macros per Day
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=dates, y=protein, name='Protein',
                        marker=dict(color=macro_colors['Protein']),
                        hovertemplate=(
                            '<b>Protein:</b> %{y} g<extra></extra>'
                        )))
    fig3.add_trace(go.Bar(x=dates, y=carbs, name='Carbs',
                        marker=dict(color=macro_colors['Carbs']),
                        hovertemplate=(
                            '<b>Carbs:</b> %{y} g<extra></extra>'
                        )))
    fig3.add_trace(go.Bar(x=dates, y=fats, name='Fats',
                        marker=dict(color=macro_colors['Fats']),
                        hovertemplate=(
                            '<b>Fats:</b> %{y} g<extra></extra>'
                        )))
    fig3.update_layout(barmode='group', title='Macros per Day')
    bar_chart = plot(fig3, output_type='div', include_plotlyjs=False)

    return render(request, 'history/history.html', {
        'line_plot': line_plot,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
        'summary': {
            'calories': round(sum(calories)/count_valid_days,2),
            'protein': round(total_protein/count_valid_days,2),
            'carbs': round(total_carbs/count_valid_days,2),
            'fats': round(total_fats/count_valid_days,2),
        },
        'cal_ranges':{
            'max_calories_day': max_calories_day,
            'max_calories_value': round(max_calories_value,2),
            'min_calories_day': min_calories_day,
            'min_calories_value': round(min_calories_value,2),
        },
        'today': datetime.today().strftime('%Y-%m-%d'),
        'days': days,
        'start_date': start_date_dt.isoformat(),
        'end_date': end_date_dt.isoformat(),
    })

