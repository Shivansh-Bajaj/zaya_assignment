from registration.models import Driver, Rider
from rest_framework import permissions


class DriverPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return Driver.objects.filter(user=request.user).exists()

class RiderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return Rider.objects.filter(user=request.user).exists()

class NotOnRide(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.on_ride