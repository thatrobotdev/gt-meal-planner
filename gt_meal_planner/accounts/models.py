from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    maiden_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.user.username

class MealPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    meal_swipes = models.IntegerField(default=0)
    dining_dollars = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.profile.user.username + "'s Meal Plan"
    
