from django.urls import path
from .views import *

urlpatterns = [
    path('v1/hotel', Hotel_APIView.as_view()),
    path('v1/flight', Hotel_APIView.as_view()),
    path('v1/activity', Hotel_APIView.as_view()), 
]