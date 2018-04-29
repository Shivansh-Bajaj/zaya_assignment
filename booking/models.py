from django.db import models
from registration.models import Driver, Rider



class Booking(models.Model):

    status_choice = (
        ('wait', 'waiting'),
        ('start', 'in ride'),
        ('end', 'completed'),
    )

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE)
    from_long_position = models.DecimalField(max_digits=8, decimal_places=5, blank=False, null=False)
    from_lat_position = models.DecimalField(max_digits=8, decimal_places=5, blank=False, null=False)
    to_long_position = models.DecimalField(max_digits=8, decimal_places=5, blank=False, null=False)
    to_lat_position = models.DecimalField(max_digits=8, decimal_places=5, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=status_choice, default='wait', max_length=5)
    distance = models.FloatField(default=2.0)
    fair = models.FloatField(default=16.0)
    seats = models.IntegerField(default=4)



