from django.urls import path
from .views import *

urlpatterns = [
    path('hotel', Hotel_APIView.as_view()),
    path('flight', Hotel_APIView.as_view()),
    path('activity', Hotel_APIView.as_view()), 
]