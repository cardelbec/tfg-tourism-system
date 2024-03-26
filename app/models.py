from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Hotel(models.Model):
    name = models.CharField(unique=True, blank=False, null=False, max_length=250)
    city = models.CharField(blank=False, null=False, max_length=250)
    address = models.CharField(blank=False, null=False, max_length=250)
    phone = models.CharField(unique=True, null=True, blank=True, max_length=15)
    stars = models.IntegerField(blank=False, null=False, validators=[MinValueValidator(1),
                                       MaxValueValidator(5)])
    image = models.URLField(blank=False, null=False, max_length=1000)

class Room(models.Model):
    capacity = models.IntegerField(blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

class Booking(models.Model):
    start = models.DateField(blank=False, null=False)
    end = models.DateField(blank=False, null=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

class Flight(models.Model):
    airline = models.CharField(blank=False, null=False, max_length=250)
    departure = models.CharField(blank=False, null=False, max_length=250)
    destination = models.CharField(blank=False, null=False, max_length=250)
    departureDate = models.DateField(blank=False, null=False)
    returnDate = models.DateField(blank=False, null=False)
    departureDepartureTime = models.TimeField(blank=False, null=False)
    departureArrivalTime = models.TimeField(blank=False, null=False)
    returnDepartureTime = models.TimeField(blank=False, null=False)
    returnArrivalTime = models.TimeField(blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    remainingSeats = models.IntegerField(blank=False, null=False)

class Activity(models.Model):
    title = models.CharField(blank=False, null=False, max_length=250)
    description = models.TextField(blank=False, null=False, max_length=1000)
    type = models.CharField(blank=False, null=False, max_length=250)
    city = models.CharField(blank=False, null=False, max_length=250)
    address = models.CharField(blank=False, null=False, max_length=250)
    date = models.DateField(blank=False, null=False)
    startTime = models.TimeField(blank=False, null=False)
    duration = models.IntegerField(blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    phone = models.CharField(unique=True, null=True, blank=True, max_length=15)