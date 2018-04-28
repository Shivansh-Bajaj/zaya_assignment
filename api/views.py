from django.contrib.auth import logout, get_user
from rest_framework import status
# from booking.models import Booking
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializer import (UserSerializer,
                            DriverSerializer,
                            RiderSerializer,
                            BookingSerializer)
from api.utils.view_utils import (decode_body,
                                  update_geo,
                                  get_fair,
                                  end_ride_driver,
                                  end_ride_rider,
                                  get_driver_ride,
                                  get_rider_ride
                                  )
from booking.services import driverservices
from registration.models import User, Driver, Rider
from registration.permissions import (
    DriverPermission,
    RiderPermission,
    NotOnRide
)


ds = driverservices.FindDriver()

#logout view


def logout_view(request):
    return logout(request)

# registrations views


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DriverViewSet(APIView):
    def get(self, format=None):

        driver = Driver.objects.all()
        serializer = DriverSerializer(driver, many=True)
        return Response({"status": "success", "data": serializer.data})

    def post(self, request):

        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "fail", "error": serializer.error_messages},
                        status=status.HTTP_400_BAD_REQUEST)


class RiderViewSet(APIView):

    def get(self, format=None):
        rider = Rider.objects.all()
        serializer = RiderSerializer(rider, many=True)
        return Response({"status": "success", "data": serializer.data})

    def post(self, request):
        serializer = RiderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "fail", "error": serializer.error_messages},
                        status=status.HTTP_400_BAD_REQUEST)

# Rider side Views


class BookingPoolViewSet(APIView):

    permission_classes = (IsAuthenticated, RiderPermission, NotOnRide)

    def post(self, request, format=None):
        body_data = decode_body(request)
        if not body_data.get('to_long') or not body_data.get('to_lat') or \
                not body_data.get('city') or not body_data.get('seats'):
            return Response({"status": "fail", "msg": "to_lang, to_lat, seats, city params require"})
        if body_data.get('seats') > 2:
            return Response({"status": "fail", "msg": "for pool only 2 seats are allowed"})
        long, lat, city = update_geo(body_data, request.user)
        to_long = body_data.get('to_long')
        to_lat = body_data.get('to_lat')
        drivers = ds.find_nearest(city, long, lat)
        print(city, long, lat, drivers)
        if len(drivers) == 0:
            return Response({"status": "fail", "error": "no driver near you"})
        for i in drivers:
            seats = int(ds.get_driver_seats(i[0]) or 0)
            print(seats)
            if seats >= int(body_data.get('seats')):
                serial = {
                    "from_long_position": long,
                    "from_lat_position": lat,
                    "to_long_position": to_long,
                    "to_lat_position": to_lat,
                    "status": "start",
                    "distance": i[1],
                    "fair": get_fair(i[1], pool=True),
                    "driver": i[0],
                    "rider": request.user,
                    "seats": int(body_data.get('seats'))
                 }
                booking = BookingSerializer(data=serial)
                if booking.is_valid(raise_exception=ValueError):
                    booking = booking.create(serial)
                if booking and seats - body_data.get('seats') == 0:
                    ds.del_geo(city, i[0])
                    ds.del_driver_from_pool(i[0])
                elif booking and seats - body_data.get('seats') > 0:
                    ds.set_driver_seats(i[0], seats - body_data.get('seats'))
                selected_driver = i[0]
                return Response(
                    {
                        "status": "success",
                        "msg": "Driver is on the way",
                        "driver": selected_driver,
                        "fair": booking.fair
                    })
        return Response({"status": "fail", "error": "no driver near you"})


class BookingViewSet(APIView):

    permission_classes = (IsAuthenticated, RiderPermission, NotOnRide)

    def post(self, request):
        body_data = decode_body(request)
        if not body_data.get('to_long') and not body_data.get('to_lat'):
            return Response({"status": "fail", "error": "no destination specified"})
        long, lat, city = update_geo(body_data, request.user)
        to_long = body_data.get('to_long')
        to_lat = body_data.get('to_lat')
        drivers = ds.find_nearest(city, long, lat)
        if len(drivers) == 0:
            return Response({"status": "fail", "error": "no driver near you"})
        for i in drivers:
            if int(ds.get_driver_seats(i[0]) or 0) == 4:
                serial = {
                    "from_long_position": long,
                    "from_lat_position": lat,
                    "to_long_position": to_long,
                    "to_lat_position": to_lat,
                    "status": "start",
                    "driver": i[0],
                    "rider": request.user,
                    "distance": i[1],
                    "seats": 4,
                    "fair": get_fair(i[1])
                 }
                print(serial)
                booking = BookingSerializer(data=serial)
                if booking.is_valid(raise_exception=ValueError):
                    booking = booking.create(serial)
                ds.del_driver_from_pool(i[0])
                print(ds.del_geo(city, i[0]))
                selected_driver = i[0]
                return Response({
                    "status": "success",
                    "msg": "Driver is on the way",
                    "driver": selected_driver,
                    "fair": booking.fair
                 })
        return Response({"status": "fail", "error": "no driver near you"})


class RiderAPI(APIView):

    permission_classes = (IsAuthenticated, RiderPermission,)

    def get(self, request):
        err, bookings, current_ride = get_rider_ride(request.user)
        if err:
            return Response({
                "status": "fail",
                "error": err
            })
        booking_serial = BookingSerializer(bookings, many=True)
        current_serial = BookingSerializer(current_ride, many=True)
        return Response({
            "status": "success",
            "rides": booking_serial.data,
            "current_ride": current_serial.data
         })

    def put(self, request):
        body_data = decode_body(request)
        update_geo(body_data, request.user)

        return Response({
            "status": "success",
            "msg": "updated geo position",
         })


class RiderEndApi(APIView):
    def post(self, request):
        body_data = decode_body(request)
        err, booking = end_ride_rider(request.user)
        long, lat, city = update_geo(body_data, request.user)
        current_seats = ds.get_driver_seats(request.user)
        ds.add_geo(city, long, lat, request.user)
        ds.set_driver_seats(request.user, int(current_seats or 0) + booking.seats)
        if not booking:
            return Response({
                "status": "fail",
                "error": err
            })
        return Response({
            "status": "success",
            "msg": "Thank You for choosing us",
            "fair": booking.fair
         })

# Driver side views


class DriverAPI(APIView):

    permission_classes = (IsAuthenticated, DriverPermission,)

    def get(self, request):
        err, bookings, current_ride = get_driver_ride(request.user)
        if err:
            return Response({
                "status": "fail",
                "error": err
            })
        booking_serial = BookingSerializer(bookings, many=True)
        current_serial = BookingSerializer(current_ride, many=True)
        return Response({
            "status": "success",
            "msg": "Thank You for choosing us",
            "rides": booking_serial.data,
            "current_ride": current_serial.data
         })


    def put(self, request):
        body_data = decode_body(request)
        long, lat, city = update_geo(body_data, request.user)
        if len(ds.match(city, request.user)[1]) != 0:
            ds.add_geo(city, long, lat, request.user)
        return Response({"status": "success", "msg": "location updated"})


class DriverStartApi(APIView):
    permission_classes = (IsAuthenticated, DriverPermission, NotOnRide)

    def post(self, request):
        body_data = decode_body(request)
        long, lat, city = update_geo(body_data, request.user)
        print(long, lat, city)
        drivers = ds.find_nearest(city, long, lat)
        print(city, long, lat, drivers)
        ds.add_geo(city, long, lat, request.user)
        ds.set_driver_seats(request.user, 4)
        return Response({"status": "success", "msg": "you are in queue we are searching for rider near you"})


class DriverStopApi(APIView):
    permission_classes = (IsAuthenticated, DriverPermission, NotOnRide)

    def post(self, request):
        # body_data = decode_body(request)
        # long, lat, city = update_geo(body_data, request.user)
        # print(long, lat, city)
        # drivers = ds.find_nearest(city, long, lat)
        # print(city, long, lat, drivers)
        # ds.add_geo(city, long, lat, request.user)
        # ds.set_driver_seats(request.user, 4)
        ds.del_driver_from_pool(request.user.username)
        ds.del_geo(request.user.city, request.user.username)
        return Response({"status": "success", "msg": "thank you for working with us"})


class DriverEndApi(APIView):
    permission_classes = (IsAuthenticated, DriverPermission, )

    def post(self, request):
        body_data = decode_body(request)
        err, booking = end_ride_driver(body_data, request.user)
        long, lat, city = update_geo(body_data, request.user)
        # if len(ds.match(city, request.user)[1]) != 0:
        #     ds.add_geo(city, long, lat, request.user)
        current_seats = ds.get_driver_seats(request.user)
        ds.add_geo(city, long, lat, request.user)
        ds.set_driver_seats(request.user, int(current_seats or 0) + booking.seats)
        if not booking:
            return Response({
                "status": "fail",
                "error": err
            })
        return Response({
            "status": "success",
            "msg": "Thank You for choosing us",
            "fair": booking.fair
         })

# social Auth


class SocialAuth(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.GET.get('param'):
            return Response({
                "status": "fail",
                "error": "param attribute is require"
            })
        [long, lat, city,type_user] = request.GET.get("param").split(",")
        if not long or not lat or not type_user or not city:
            return Response({
                "status": "fail",
                "error": "param attribute is long, lat, city, type(driver, rider) require"
            })
        request.user.long_position, request.user.lat_position = long, lat
        request.user.city = city
        request.user.save()
        if type_user == "driver":
            Driver(user=get_user(request)).save()
            request.user.is_driver = True
            request.user.save()
        elif type_user == "rider":
            Rider(user=get_user(request)).save()
            request.user.is_rider = True
            request.user.save()
        else:
            return Response({"status": "fail", "error": "type can be driver/rider"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "success", "msg": "signup success"}, status=status.HTTP_201_CREATED)
