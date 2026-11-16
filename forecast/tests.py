from unittest.mock import patch
from django.test import TestCase

class WeatherDashboardSmokeTests(TestCase):
    @patch("forecast.views.get_hourly", return_value=[])
    @patch("forecast.views.get_7_days_history_api", return_value=[])
    @patch("forecast.views.get_current", return_value=None)
    @patch("forecast.views.get_lat_lon", return_value=(-6.4, 106.1))
    @patch("forecast.views.TENSORFLOW_AVAILABLE", new=False)
    def test_dashboard_renders_without_optional_weather_api_key(
        self, _lat_lon, _current, _history, _hourly
    ):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Weather Dashboard")
        self.assertContains(response, "Historical baseline")

    @patch("forecast.views.get_current", return_value=None)
    @patch("forecast.views.get_lat_lon", return_value=(-6.4, 106.1))
    def test_weather_api_returns_controlled_error_without_provider_key(self, _lat_lon, _current):
        response = self.client.get("/api/weather/?city=Banten")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False})

    @patch("forecast.views.get_3_hourly", return_value=[])
    @patch("forecast.views.get_recent_hourly", return_value=([], [], [], []))
    @patch("forecast.views.get_current", return_value=None)
    @patch("forecast.views.get_lat_lon", return_value=(-6.4, 106.1))
    def test_city_detail_page_renders_without_provider_key(
        self, _lat_lon, _current, _recent, _three_hourly
    ):
        response = self.client.get("/weather/Serang/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Serang")
