from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    maiden_name = models.CharField(max_length=255)
    dining_dollars = models.IntegerField()
    meal_swipes = models.IntegerField()

    def __str__(self):
        return self.user.username
