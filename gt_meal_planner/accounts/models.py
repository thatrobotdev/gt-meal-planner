from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    maiden_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.username

class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    meal_swipes = models.IntegerField(default=0)
    dining_dollars = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    current_swipes = models.IntegerField(default=0)
    current_dollars = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username + "'s Meal Plan"

class Purchase(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='purchases')
    swipe_cost = models.IntegerField(default=0)
    dollars_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    date = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.meal_plan.user.username}'s Purchase - {self.swipe_cost} swipes, ${self.dollars_cost} on {self.date}"
