from django.contrib import admin
from accounts.models import MealPlan
from accounts.models import Purchase
# Register your models here.
admin.site.register(MealPlan)
admin.site.register(Purchase)