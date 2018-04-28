from registration.models import Driver, Rider
from rest_framework import permissions


class DriverPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_driver

class RiderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_rider

class NotOnRide(permissions.BasePermission):
    def has_permission(self, request, view):
        print(request.user.on_ride, "permissions")
        return not request.user.on_ride