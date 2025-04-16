import random
from django.shortcuts import render
from accounts.models import MealPlan, Purchase
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from decimal import Decimal
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db import models
from django.utils import timezone

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

            total_days = (latest_meal_plan.end_date - latest_meal_plan.start_date).days
            day_count = (date.today() - latest_meal_plan.start_date).days

            ideal_dining_dollars = latest_meal_plan.dining_dollars / total_days
            ideal_swipes = latest_meal_plan.meal_swipes / total_days
            avg_dining_dollars = (latest_meal_plan.dining_dollars - latest_meal_plan.current_dollars) / day_count
            avg_swipes = (latest_meal_plan.meal_swipes - latest_meal_plan.current_swipes) / day_count

            template_data['ideal'] = ideal_dining_dollars
            template_data['avg'] = avg_dining_dollars

            template_data['dining_dollars_rate'] = 0
            if avg_dining_dollars > ideal_dining_dollars + 1:
                template_data['dining_dollars_rate'] = 1
            elif avg_dining_dollars < ideal_dining_dollars - 1:
                template_data['dining_dollars_rate'] = -1
            
            template_data['swipes_rate'] = 0
            if avg_swipes > ideal_swipes + 0.5:
                template_data['swipes_rate'] = 1
            elif avg_swipes < ideal_swipes - 0.5:
                template_data['swipes_rate'] = -1

        else:
            template_data['active'] = False
    else:
        template_data['active'] = False
    if template_data['active']:
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        purchases = latest_meal_plan.purchases.all()
        current_date = date.today()
        swipes_left = latest_meal_plan.current_swipes
        dollars_left = latest_meal_plan.current_dollars
        days_left = (latest_meal_plan.end_date - current_date).days
        recommended_swipes = swipes_left // days_left
        recommended_dollars = dollars_left / days_left
        dates = []
        spentSwipes = []
        spentDollars = []
        for i in range (6, -1, -1):
            curr = current_date - timedelta(days=i)
            curr_purchases = purchases.filter(date=curr)
            currSwipes = 0
            currDollars = Decimal(0)
            for p in curr_purchases:
                currSwipes += p.swipe_cost
                currDollars += p.dollars_cost
            dates.append(curr)
            spentSwipes.append(currSwipes)
            spentDollars.append(currDollars)
        #create plots for weekly dining dollar spending and meal swipe spending
        figWS, axWS = plt.subplots()
        figWD, axWD = plt.subplots()
        #add graph titles
        axWS.set_title('Weekly Meal Swipe Spending')
        axWD.set_title('Weekly Dining Dollar Spending')
        #add data to bar graphs (still need to generate the data)
        axWS.bar(dates, spentSwipes)
        axWD.bar(dates, spentDollars)
        #format the dates on graph to only display month and day
        axWS.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        axWD.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        #add recommended spending to graph
        axWS.axhline(y=recommended_swipes, color='red', linestyle='--', linewidth=2, label='TargetSwipes')
        axWD.axhline(y=recommended_dollars, color='red', linestyle='--', linewidth=2, label='TargetDollars')
        figWS.text(0.5, 0.01, 'Recommended Weekly Budget: ' + str(recommended_swipes * 7) + ' Swipes', ha='center', fontsize=10, color='gray')
        figWD.text(0.5, 0.01, 'Recommended Weekly Budget: $' + str(recommended_dollars * 7), ha='center', fontsize=10, color='gray')
        #store images of graphs
        bufWS = BytesIO()
        bufWD = BytesIO()
        figWS.savefig(bufWS, format='png')
        figWD.savefig(bufWD, format='png')
        bufWS.seek(0)
        bufWD.seek(0)
        encoded_WS = base64.b64encode(bufWS.read()).decode('utf-8')
        encoded_WD = base64.b64encode(bufWD.read()).decode('utf-8')
        bufWS.close()
        bufWD.close()
        template_data['weeklySwipeChart'] = encoded_WS
        template_data['weeklyDollarChart'] = encoded_WD



    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})