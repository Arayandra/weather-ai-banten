from django.urls import path
from .views import weather_api
from . import views

urlpatterns = [
    # Halaman Utama (Dashboard)
    path('', views.weather_view, name='weather_dashboard'),
    
    path('weather/<str:city>/', views.city_detail_view, name='weather_detail'),
    
    # API
    path('api/weather/', weather_api, name='weather_api'),
]