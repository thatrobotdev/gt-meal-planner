import random
from django.shortcuts import render
from accounts.models import MealPlan
from django.contrib.auth.models import User
from datetime import datetime, date

def index(request):
    user = request.user
    template_data = {}
    if user.is_authenticated:
        template_data['username'] = user.username
        if user.meal_plans.exists():
            latest_meal_plan = user.meal_plans.order_by('-start_date').first()
            start = latest_meal_plan.start_date
            end = latest_meal_plan.end_date
            check_start = date(2025, 1, 3)
            if end < check_start:
                template_data['active'] = False
            else:
                template_data['active'] = True
                template_data['swipes'] = latest_meal_plan.current_swipes
                template_data['dollars'] = latest_meal_plan.current_dollars
                template_data['start'] = latest_meal_plan.start_date
                template_data['end'] = latest_meal_plan.end_date
        else:
            template_data['active'] = False
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})