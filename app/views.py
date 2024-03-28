from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import HotelSerializers, FlightSerializers, ActivitySerializers
from .models import Hotel, Room, Booking, Flight, Activity
from drf_spectacular.utils import extend_schema

class Hotel_APIView(APIView):

    @extend_schema(responses= HotelSerializers(many=True))
    def get(self, request, format=None, *args, **kwargs):
        hotels = Hotel.objects.all()
        serializer = HotelSerializers(hotels, many=True)
        
        return Response(serializer.data)

class Flight_APIView(APIView):

    @extend_schema(responses= FlightSerializers(many=True))
    def get(self, request, format=None, *args, **kwargs):
        flights = Flight.objects.all()
        serializer = FlightSerializers(flights, many=True)
        
        return Response(serializer.data)
    
class Activity_APIView(APIView):

    @extend_schema(responses= ActivitySerializers(many=True))
    def get(self, request, format=None, *args, **kwargs):
        activities = Activity.objects.all()
        serializer = ActivitySerializers(activities, many=True)
        
        return Response(serializer.data)