import random
from django.shortcuts import render
from accounts.models import MealPlan

def index(request):
    user = request.user
    template_data = {}
    if user.is_authenticated:
        meal_plan = MealPlan.objects.filter(user=user).first()
        template_data['meal'] = meal_plan
        if meal_plan:
            template_data['swipes'] = meal_plan.meal_swipes
            template_data['dollars'] = meal_plan.dining_dollars
            template_data['start'] = meal_plan.start_date
            template_data['end'] = meal_plan.end_date
        template_data['username'] = user.username
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})