from django.urls import path
from . import views

urlpatterns = [
    path("", views.weather_view, name="weather_dashboard"),
    path("weather/<str:city>/", views.city_detail_view, name="weather_detail"),
    path("api/weather/", views.weather_api, name="weather_api"),
]
