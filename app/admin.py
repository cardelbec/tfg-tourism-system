from django.contrib import admin
from .models import Hotel, Room, Booking, Flight, Activity

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Flight)
admin.site.register(Activity)