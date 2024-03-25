from rest_framework import serializers
from .models import Hotel, Room, Booking, Flight, Activity

class HotelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class FlightSerializers(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class ActivitySerializers(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'