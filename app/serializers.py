from rest_framework import serializers
from .models import Hotel, Room, Flight, Activity

class HotelSerializers(serializers.ModelSerializer):
    price = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Hotel
        fields = ['name','city','address','phone','stars','price']

class RoomSerializers(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_hotel_name')
    address = serializers.SerializerMethodField('get_hotel_address')
    phone = serializers.SerializerMethodField('get_hotel_phone')
    stars = serializers.SerializerMethodField('get_hotel_stars')

    class Meta:
        model = Room
        fields = ['capacity', 'price', 'name', 'address', 'phone', 'stars']

    def get_hotel_name(self, room):
        name = room.hotel.name
        return name
    
    def get_hotel_address(self, room):
        address = room.hotel.address
        return address
    
    def get_hotel_phone(self, room):
        phone = room.hotel.phone
        return phone
    
    def get_hotel_stars(self, room):
        stars = room.hotel.stars
        return stars

class FlightSerializers(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class ActivitySerializers(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'