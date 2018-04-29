from registration.models import User, Driver, Rider
from booking.models import Booking
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'long_position', 'lat_position', 'password', 'city', 'on_ride')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            long_position=validated_data['long_position'],
            lat_position=validated_data['lat_position'],
            city=validated_data['city'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class BookingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Booking
        fields = ('from_lat_position', 'from_long_position',
                  'to_long_position', 'to_lat_position', 'status', 'distance', 'fair', 'seats', 'created_at')

    def create(self, validated_data):
        try:

            driver_user = User.objects.get(username=validated_data['driver'])
            driver = Driver.objects.get(user=driver_user)
            driver_user.on_ride = True
            driver_user.save()
            rider = Rider.objects.get(user=validated_data['rider'])
            validated_data['rider'].on_ride = True
            validated_data['rider'].save()
        except Exception as e:
            raise e

        booking = Booking(
            from_long_position=validated_data["from_long_position"],
            from_lat_position=validated_data["from_lat_position"],
            to_long_position=validated_data["to_long_position"],
            to_lat_position=validated_data["to_lat_position"],
            status=validated_data["status"],
            distance=validated_data["distance"],
            fair=validated_data["fair"],
            driver=driver,
            rider=rider,
            seats=validated_data["seats"]
        )
        booking.save()
        return booking


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Driver
        fields = ('user',)

    def create(self, validated_data):

        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user.is_driver = True
        user.save()
        driver, created = Driver.objects.update_or_create(user=user)
        return driver


class RiderSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Rider
        fields = ('user',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        user.is_rider = True
        user.save()
        rider, created = Rider.objects.update_or_create(user=user)
        return rider
