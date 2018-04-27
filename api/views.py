from api.serializer import (UserSerializer,
                            DriverSerializer,
                            RiderSerializer,
                            BookingSerializer)
from api.utils.view_utils import (decode_body,
                                  update_geo,
                                  get_my_ride,
                                  get_fair,
                                  end_ride)
from booking.services import driverservices
from registration.models import User, Driver, Rider
# from booking.models import Booking
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from registration.permissions import (
    DriverPermission,
    RiderPermission
)
from django.contrib.auth import logout

ds = driverservices.FindDriver()


def logout_view(request):
    logout(request)


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


class BookingPoolViewSet(APIView):

    permission_classes = (IsAuthenticated, RiderPermission,)

    def post(self, request):
        body_data = decode_body(request)
        if not body_data.get('to_long') and not body_data.get('to_lat') and not body_data.get('seats'):
            return Response({"status": "fail", "msg": "no destination specified"})
        if body_data.get('seats') > 2:
            return Response({"status": "fail", "msg": "for pool only 2 seats are allowed"})
        long, lat, city = update_geo(body_data, request.user)
        to_long = body_data.get('to_long')
        to_lat = body_data.get('to_lat')
        drivers = ds.find_nearest(city, long, lat)
        if len(drivers) == 0:
            return Response({"status": "fail", "error": "no driver near you"})
        for i in drivers:
            seats = int(ds.get_driver_seats(i[0]) or 0)
            if seats <= body_data.get('seats'):
                serial = {
                    "from_long_position": long,
                    "from_lat_position": lat,
                    "to_long_position": to_long,
                    "to_lat_position": to_lat,
                    "status": "start",
                    "driver": i[0],
                    "rider": request.user
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
                    })
        return Response({"status": "fail", "error": "no driver near you"})


class BookingViewSet(APIView):

    permission_classes = (IsAuthenticated, RiderPermission,)

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
                    "fair": get_fair(i[1])
                 }
                print(serial)
                booking = BookingSerializer(data=serial)
                if booking.is_valid(raise_exception=ValueError):
                    booking = booking.create(serial)
                ds.del_driver_from_pool(i[0])
                print(ds.del_geo(city, i[0]))
                selected_driver = i[0]
                return Response({"status": "success",
                                 "msg": "Driver is on the way",
                                 "driver": selected_driver
                                 })
        return Response({"status": "fail", "error": "no driver near you"})


class DriverAPI(APIView):

    permission_classes = (IsAuthenticated, DriverPermission,)

    def post(self, request):
        body_data = decode_body(request)
        long, lat, city = update_geo(body_data, request.user)
        ds.add_geo(city, long, lat, request.user)
        ds.set_driver_seats(request.user, 4)
        return Response({"status": "success", "msg": "you are in queue we are searching for rider near you"})

    def put(self, request):
        body_data = decode_body(request)
        long, lat, city = update_geo(body_data, request.user)
        if len(ds.match(city, request.user)[1]) != 0:
            ds.add_geo(city, long, lat, request.user)
        return Response({"status": "success", "msg": "location updated"})


class CompletedRide(APIView):
    def get(self, request):
        rides, on_ride, current_ride = get_my_ride(request, 'rider')
        print(rides, on_ride, current_ride)
        if not on_ride:
            return Response({"success": "fail", "error": "you are not currently on ride"})
        end_ride(current_ride)
        return Response({"successs"})


class SocialAuth(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print(request)
        print(request.data, request.user)
        return Response('success')
