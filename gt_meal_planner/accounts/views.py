from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import MealPlan
from accounts.models import Purchase
from datetime import datetime, date
from decimal import Decimal

def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['failed_attempts'] = 0
            return redirect('orders')
        else:
            failed_attempts = request.session.get('failed_attempts', 0) + 1
            request.session['failed_attempts'] = failed_attempts
            context['error'] = "Invalid username or password."
            if failed_attempts >= 1:
                context['login_failed'] = True

    return render(request, 'login.html', {'template_data': context})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            check_start = date(2025, 1, 3)
            check_end = date(2025, 5, 1)
            if user.meal_plans.exists():
                latest_meal_plan = user.meal_plans.order_by('-start_date').first()
                start = latest_meal_plan.start_date
                end = latest_meal_plan.end_date
                if end < check_start:
                    return redirect('accounts.baseplans')
                return redirect('home.index')
            return redirect('accounts.baseplans')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        maiden_name = request.POST.get('maiden_name')
        new_password = request.POST.get('new_password')

        try:
            user = User.objects.get(username=username)
            if user.profile.maiden_name.lower() == maiden_name.lower():  # Assuming the field is in the profile model
                user.set_password(new_password)
                user.save()
                return redirect('accounts.login')
            else:
                return render(request, 'accounts/reset_password.html', {'error': 'Incorrect security answer'})
        except User.DoesNotExist:
            return render(request, 'accounts/reset_password.html', {'error': 'User not found'})

    return render(request, 'accounts/reset_password.html')

def baseplans(request):
    template_data = {}
    user = request.user
    if user.meal_plans.exists():
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        start = latest_meal_plan.start_date
        end = latest_meal_plan.end_date
        check_start = date(2025, 1, 3)
        if end < check_start:
            template_data['active'] = False
        else:
            template_data['active'] = True
    else:
        template_data['active'] = False

    if request.method == 'POST':
        print(request.POST.get('dollars'))
        user = request.user
        meal_plan, created = MealPlan.objects.get_or_create(user=user)
        meal_swipes = request.POST.get('swipes')
        dining_dollars = request.POST.get('dollars')
        meal_plan.meal_swipes = int(meal_swipes)
        meal_plan.dining_dollars = float(dining_dollars)
        meal_plan.start_date = datetime.strptime("03/01/2025", "%d/%m/%Y").date()
        meal_plan.end_date = datetime.strptime("01/05/2025", "%d/%m/%Y").date()
        meal_plan.current_dollars = meal_plan.dining_dollars
        meal_plan.current_swipes = meal_plan.meal_swipes
        meal_plan.save()
        return redirect('home.index')
    return render(request, 'accounts/baseplans.html', {'template_data': template_data})

def map(request):
    template_data = {}
    return render(request, 'accounts/map.html', {'template_data': template_data})

def inputspending(request):
    template_data = {}
    user = request.user
    if user.meal_plans.exists():
        check_start = date(2025, 1, 3)
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        if latest_meal_plan.end_date < check_start:
            template_data['active'] = False
        else:
            template_data['active'] = True
    else:
        template_data['active'] = False
    if request.method == 'POST':
        spending_type = request.POST.get('spending_type')
        swipes = 0
        dollars = Decimal('0.00')
        if spending_type == 'swipes':
            swipes = int(request.POST.get('swipes'))
        else:
            dollars = Decimal(request.POST.get('dining_dollars'))
        purchase_date_str = request.POST.get('plan_start')
        purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        if purchase_date < latest_meal_plan.start_date or purchase_date > latest_meal_plan.end_date:
            template_data['badDate'] = True
            template_data['startDate'] = latest_meal_plan.start_date.strftime("%Y-%m-%d")
            template_data['endDate'] = latest_meal_plan.end_date.strftime("%Y-%m-%d")
            return render(request, 'accounts/inputspending.html', {'template_data': template_data})
        if latest_meal_plan.current_swipes - swipes < 0:
            template_data['badSwipes'] = True
            template_data['leftSwipes'] = latest_meal_plan.current_swipes
            return render(request, 'accounts/inputspending.html', {'template_data': template_data})
        if latest_meal_plan.current_dollars - dollars < 0:
            template_data['badDollars'] = True
            template_data['leftDollars'] = latest_meal_plan.current_dollars
            return render(request, 'accounts/inputspending.html', {'template_data': template_data})
        #purchase is valid at this point
        latest_meal_plan.current_dollars -= dollars
        latest_meal_plan.current_swipes -= swipes
        latest_meal_plan.save()
        Purchase.objects.create(
            meal_plan=latest_meal_plan,
            swipe_cost=swipes,
            dollars_cost=dollars,
            date=purchase_date
        )

        return redirect('home.index')
    return render(request, 'accounts/inputspending.html', {'template_data': template_data})

def purchasehistory(request):
    template_data = {}
    user = request.user
    if user.meal_plans.exists():
        check_start = date(2025, 1, 3)
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        if latest_meal_plan.end_date < check_start:
            template_data['active'] = False
        else:
            template_data['active'] = True
    else:
        template_data['active'] = False
    if template_data['active']:
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        if latest_meal_plan.purchases.exists():
            template_data['noPurchases'] = False
        else:
            template_data['noPurchases'] = True
    else:
        template_data['noPurchases'] = True
    if not template_data['noPurchases']:
        #add purchases to template data
        #create front end for them with edit buttons
        latest_meal_plan = user.meal_plans.order_by('-start_date').first()
        template_data['purchases'] = latest_meal_plan.purchases.order_by('-date').all()
    if request.method == "POST":
        purchase_id = request.POST.get("purchase_id")
        print(purchase_id)
        return redirect('accounts.editpurchase', purchase_id = purchase_id)
    return render(request, 'accounts/purchasehistory.html', {'template_data': template_data})
def editpurchase(request, purchase_id):
    template_data = {}
    user = request.user
    purchase = Purchase.objects.get(id=purchase_id)
    if not purchase.meal_plan.user == user:
        template_data['validate'] = False
    else:
        template_data['validate'] = True
    if template_data['validate']:
        template_data['date'] = purchase.date
        template_data['oldSwipes'] = purchase.swipe_cost
        template_data['oldDollars'] = purchase.dollars_cost
    if request.method == "POST":
        if request.POST.get("delete") == "true":
            latest_meal_plan = user.meal_plans.order_by('-start_date').first()
            latest_meal_plan.current_dollars += purchase.dollars_cost
            latest_meal_plan.current_swipes += purchase.swipe_cost
            latest_meal_plan.save()
            purchase.delete()
            return redirect('accounts.purchasehistory')
        else:
            #adjust meal plan current swipes and dollars
            #save meal plan and purchase changes
            newSwipes = int(request.POST.get("swipes"))
            newDollars = Decimal(request.POST.get("dining_dollars"))
            newDate = datetime.strptime(request.POST.get("date"), "%Y-%m-%d").date()
            latest_meal_plan = user.meal_plans.order_by('-start_date').first()
            if newDate < latest_meal_plan.start_date or newDate > latest_meal_plan.end_date:
                template_data['invalidDate'] = True
                return render(request, 'accounts/editpurchase.html', {'template_data': template_data})
            if latest_meal_plan.current_swipes + purchase.swipe_cost - newSwipes < 0:
                template_data['invalidSwipes'] = True
                return render(request, 'accounts/editpurchase.html', {'template_data': template_data})
            if latest_meal_plan.current_dollars + purchase.dollars_cost - newDollars < 0:
                template_data['invalidDollars'] = True
                return render(request, 'accounts/editpurchase.html', {'template_data': template_data})
            latest_meal_plan.current_swipes += purchase.swipe_cost
            latest_meal_plan.current_swipes -= newSwipes
            latest_meal_plan.current_dollars += purchase.dollars_cost
            latest_meal_plan.current_dollars -= newDollars
            latest_meal_plan.save()
            purchase.swipe_cost = newSwipes
            purchase.dollars_cost = newDollars
            purchase.date = newDate
            purchase.save()
            return redirect('accounts.purchasehistory')
    return render(request, 'accounts/editpurchase.html', {'template_data': template_data})