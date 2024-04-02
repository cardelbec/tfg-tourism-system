from django.urls import path
from .views import *

urlpatterns = [
    path('hotel/', Hotel_APIView.as_view()),
    path('flight/', Flight_APIView.as_view()),
    path('activity/', Activity_APIView.as_view()),
    path('activityType/', ActivityType_APIView.as_view()),
    path('webhook/', handleWebhook),
]