import json
from registration.models import User, Driver, Rider
from booking.models import Booking, RiderBookingTable
from cabbookingapp.settings import FAIR_PER_KM, POOL_FAIR_PER_KM


def decode_body(request):
    body_data = {}
    print(request.POST)
    body_unicode = request.body.decode('utf-8')
    print(body_unicode)
    if body_unicode != '':
        body_data = json.loads(body_unicode)
    return body_data


def get_fair(distance, pool=False):
    if pool:
        return float(distance) * POOL_FAIR_PER_KM
    return float(distance) * FAIR_PER_KM

# update Geo position


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

# fetch profile info


def get_rider_ride(user):
    try:
        rider = Rider.objects.get(user=user)
        bookings = RiderBookingTable.objects.filter(rider=rider).order_by("created_at")
    except Exception as e:
        raise e
    current_ride = None
    if len(bookings) == 0:
        return "no ride found", None, None
    if user.on_ride:
        current_ride = bookings.last()
    booking_result = []
    for i in bookings:
        booking_result.append(i)
    return None, booking_result, current_ride.booking


def get_driver_ride(user):
    try:
        driver = Driver.objects.get(user=user)
        bookings = Booking.objects.filter(driver=driver).order_by("created_at")
    except Exception as e:
        raise e
    current_booking = None
    if len(bookings) == 0:
        return "no ride found", None, None
    if user.on_ride:
        current_booking = []
        for i in bookings:
            if i.status == "start":
                current_booking.append(i)
    return None, bookings, current_booking

# end current ride


def end_ride_rider(user):
    if not user.on_ride:
        return "you are not on a ride", None
    try:
        rider = Rider.objects.get(user=user)
        bookings = RiderBookingTable.objects.filter(rider=rider).order_by("created_at")
    except Exception as e:
        raise e
    if len(bookings) == 0:
        return "no ride found", None
    current_ride = bookings.last()
    current_ride.booking.driver.user.on_ride = False
    current_ride.booking.driver.user.long_position = current_ride.booking.to_long_position
    current_ride.booking.driver.user.lat_position = current_ride.booking.to_lat_position
    current_ride.booking.driver.user.save()
    current_ride.booking.status = "end"
    current_ride.booking.save()
    user.lat_position = current_ride.booking.to_lat_position
    user.long_position = current_ride.booking.to_long_position
    user.save()
    return None, current_ride.booking


def end_ride_driver(body_data, user):
    if not user.on_ride:
        return "you are not on a ride", None

    try:
        driver = Driver.objects.get(user=user)
        booking = Booking.objects.get(driver=driver, status="start")
    except Exception as e:
        raise e
    try:
        riders = RiderBookingTable.objects.filter(booking=booking)
    except Exception as e:
        raise e
    if len(riders) == 1:
        riders[0].rider.user.on_ride = False
        riders[0].rider.user.lat_position = booking.to_lat_position
        riders[0].rider.user.long_position = booking.to_long_position
        riders[0].rider.user.save()
    elif body_data.rider_name not in ['', None]:
        for i in riders:
            rider = None
            if i.rider.user.username == body_data.ridername:
                rider = i
                break
        if rider == None:
            return "rider_name not found", None
        rider.rider.user.on_ride = False
        rider.rider.user.lat_position = booking.to_lat_position
        rider.rider.user.long_position = booking.to_long_position
        rider.rider.user.save()
    else:
        return "rider_name field required in pool booking", None
    booking.status = "end"
    booking.save()
    driver.user.on_ride = False
    driver.user.long_position = booking.to_long_position
    driver.user.lat_position = booking.to_lat_position
    driver.user.save()
    return None, booking

