from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    is_driver = models.BooleanField(default=False)
    is_rider = models.BooleanField(default=False)
    long_position = models.DecimalField(max_digits=8, decimal_places=5, null=True)
    lat_position = models.DecimalField(max_digits=8, decimal_places=5, null=True)
    city = models.CharField(max_length=100, default="None")
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    on_ride = models.BooleanField(default=False)

class Rider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    on_ride = models.BooleanField(default=False)