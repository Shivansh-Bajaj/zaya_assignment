import json
from registration.models import User, Driver, Rider
from booking.models import DriverBookingTable, RiderBookingTable
from cabbookingapp.settings import FAIR_PER_KM

def decode_body(request):
    body_data = {}
    body_unicode = request.body.decode('utf-8')
    print(body_unicode)
    if body_unicode != '':
        body_data = json.loads(body_unicode)
    return body_data


def update_geo(body_data, user):

    if body_data.get('long') and body_data.get('lat') and body_data.get('city'):
        long = body_data.get('long')
        lat = body_data.get('lat')
        city = body_data.get('city')
        try:
            user = User.objects.get(username=user)
        except Exception as e:
            raise e
        user.long_position = long
        user.lat_position = lat
        user.city = city
        user.save()
    else:
        try:
            user = User.objects.get(username=user)
        except Exception as e:
            raise e
        long = user.long_position
        lat = user.lat_position
        city = user.city
        return long, lat, city


def get_my_ride(request, user_type):
    obj = None
    table = None
    if user_type == 'driver':
        try:
            obj = Driver.objects.get(user=request.user)
            table = DriverBookingTable.objects.filter(driver=obj).order_by('created_at')
        except Exception as e:
            raise e
    elif user_type == 'rider':
        try:
            obj = Rider.objects.get(user=request.user)
            table = RiderBookingTable.objects.filter(rider=obj).order_by('created_at')
        except Exception as e:
            raise e

    if table and obj and not obj.on_ride:
        return table, False, None
    elif table and obj and obj.on_ride:
        return table, True, table[0]

def end_ride(ride):
    print(ride.booking)

def get_fair(distance):
    print(distance)
    return float(distance) * FAIR_PER_KM