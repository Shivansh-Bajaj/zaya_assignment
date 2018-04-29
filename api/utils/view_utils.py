import json
from registration.models import User, Driver, Rider
from booking.models import Booking
from cabbookingapp.settings import FAIR_PER_KM, POOL_FAIR_PER_KM


def decode_body(request):
    body_data = {}
    body_unicode = request.body.decode('utf-8')
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
        bookings = Booking.objects.filter(rider=rider).order_by("created_at")
    except Exception as e:
        raise e
    current_ride = None
    if len(bookings) == 0:
        return "no ride found", None, None
    if user.on_ride:
        for i in bookings:
            if i.status == "start":
                current_ride = i
            break

    return None, bookings, current_ride


def get_driver_ride(user):
    try:
        driver = Driver.objects.get(user=user)
        bookings = Booking.objects.filter(driver=driver).order_by("created_at")
    except Exception as e:
        raise e

    current_booking = None
    if len(bookings) == 0:
        return "no ride found", None, None
    users = []
    if user.on_ride:
        current_booking = []
        for i in bookings:
            if i.status == "start":
                current_booking.append(i)
                users.append(i.rider)
    return None, bookings, current_booking, users

# end current ride


def end_ride_rider(user):
    if not user.on_ride:
        return "you are not on a ride", None
    try:
        rider = Rider.objects.get(user=user)
        bookings = Booking.objects.filter(rider=rider, status="start").order_by("created_at")
    except Exception as e:
        raise e
    if len(bookings) == 0:
        return "no ride found", None
    for current_ride in bookings:
        try:
            driver_booking = Booking.objects.filter(driver=current_ride.driver, status="start")
            if len(driver_booking) == 1:
                current_ride.driver.user.on_ride = False
        except Exception as e:
            raise e
        current_ride.driver.user.long_position = current_ride.to_long_position
        current_ride.driver.user.lat_position = current_ride.to_lat_position
        current_ride.driver.user.save()
        current_ride.status = "end"
        current_ride.save()
        user.lat_position = current_ride.to_lat_position
        user.long_position = current_ride.to_long_position

    user.on_ride = False
    user.save()
    return None, current_ride


def end_ride_driver(body_data, user):
    if not user.on_ride:
        return "you are not on a ride", None

    try:
        driver = Driver.objects.get(user=user)
        booking = Booking.objects.filter(driver=driver, status="start")
    except Exception as e:
        raise e

    if len(booking) == 1:
        booking[0].rider.user.on_ride = False
        booking[0].rider.user.lat_position = booking[0].to_lat_position
        booking[0].rider.user.long_position = booking[0].to_long_position
        booking[0].rider.user.save()
        driver.user.on_ride = False
        driver.user.long_position = booking[0].to_long_position
        driver.user.lat_position = booking[0].to_lat_position
        booking[0].status = "end"
        booking[0].save()
        end_booking = booking[0]
    elif body_data.get('rider_name') not in ['', None]:
        rider = None
        for i in booking:
            if i.rider.user.username == body_data.get('rider_name'):
                rider = i
                rider.rider.user.on_ride = False
                rider.rider.user.lat_position = i.to_lat_position
                rider.rider.user.long_position = i.to_long_position
                i.status = "end"
                i.save()
                driver.user.long_position = i.to_long_position
                driver.user.lat_position = i.to_lat_position
                rider.rider.user.save()
                end_booking = i
                break
        if rider == None:
            return "rider_name not found", None
    else:
        return "rider_name field required in pool booking", None


    driver.user.save()
    return None, end_booking

