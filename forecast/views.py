from django.shortcuts import render
from django.http import JsonResponse

import os, json, requests, joblib
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, timedelta

# TensorFlow is optional at import time so Django's admin/check commands can run
# even before the AI runtime is installed. Full predictions require requirements.txt.
try:
    import tensorflow as tf
    from keras.models import load_model
    from keras.layers import Layer
    from keras.saving import register_keras_serializable
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    load_model = None
    Layer = object
    TENSORFLOW_AVAILABLE = False

    def register_keras_serializable(*args, **kwargs):
        def decorator(obj):
            return obj
        return decorator

# ==============================================================================
# DAFTAR KOMPONEN KUSTOM AI
# ==============================================================================
@register_keras_serializable()
def asymmetric_loss(y_true, y_pred):
    if tf is None:
        raise RuntimeError("TensorFlow belum terpasang. Install requirements.txt untuk prediksi AI.")
    error = y_true - y_pred
    penalty = tf.where(error > 0, 3.0, 1.0)
    return tf.reduce_mean(penalty * tf.square(error))


@register_keras_serializable()
class Attention(Layer):
    def __init__(self, **kwargs):
        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(
            name='attention_weight',
            shape=(input_shape[-1], 1),
            initializer='random_normal',
            trainable=True
        )

        self.b = self.add_weight(
            name='attention_bias',
            shape=(input_shape[1], 1),
            initializer='zeros',
            trainable=True
        )

        super(Attention, self).build(input_shape)

    def call(self, x):
        e = tf.tanh(tf.matmul(x, self.W) + self.b)
        a = tf.nn.softmax(e, axis=1)
        output = x * a
        return tf.reduce_sum(output, axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])


# ================= CONFIG =================
WEATHER_API_KEY = os.environ.get('WEATHERAPI_API_KEY', '').strip()

jakarta_tz = pytz.timezone('Asia/Jakarta')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

CSV_PATH = os.path.join(DATA_DIR, 'dataset_banten_clean.csv')
MODEL_PATH = os.path.join(DATA_DIR, 'model.keras')
BUNDLE_PATH = os.path.join(DATA_DIR, 'dataset_bundle.pkl')

TIME_STEPS = 31


# ================= LOAD MODEL =================
MODEL = None
BUNDLE = None


def load_ai():
    global MODEL, BUNDLE

    if not TENSORFLOW_AVAILABLE:
        raise RuntimeError("TensorFlow belum terpasang. Jalankan: pip install -r requirements.txt")

    if MODEL is None or BUNDLE is None:
        custom_objects_dict = {
            'Attention': Attention,
            'asymmetric_loss': asymmetric_loss
        }

        MODEL = load_model(
            MODEL_PATH,
            custom_objects=custom_objects_dict,
            compile=False
        )

        BUNDLE = joblib.load(BUNDLE_PATH)

    return MODEL, BUNDLE


# ================= 20 FITUR =================
FEATURES = [
    'temperature_2m_mean',
    'precipitation_sum',
    'windspeed_10m_max',
    'cape_proxy_radiation',
    'lat',
    'lon',
    'sin_month',
    'cos_month',
    'sin_day',
    'cos_day',
    'temp_lag1',
    'temp_lag2',
    'rain_lag1',
    'temp_roll3',
    'rain_roll3',
    'temp_diff',
    'rain_diff',
    'sst_anomaly',
    'enso_index',
    'iod_index'
]


# ================= ICON HELPERS =================
def get_icon(desc):
    d = desc.lower()

    if 'rain' in d or 'hujan' in d:
        return 'bi-cloud-rain-fill'

    elif 'cloud' in d or 'awan' in d:
        return 'bi-cloud-fill'

    elif 'clear' in d or 'cerah' in d:
        return 'bi-sun-fill'

    return 'bi-cloud'


def get_icon_day(temp, rain):
    if rain > 0:
        return "bi-cloud-rain-fill"

    elif temp > 30:
        return "bi-sun-fill"

    return "bi-cloud"


# ================= KONVERSI ARAH ANGIN =================
def get_wind_direction_text(degree):
    """
    Mengubah derajat angin menjadi arah mata angin
    """

    try:
        degree = float(degree)

        directions = [
            "Utara",
            "Timur Laut",
            "Timur",
            "Tenggara",
            "Selatan",
            "Barat Daya",
            "Barat",
            "Barat Laut"
        ]

        index = round(degree / 45) % 8

        return directions[index]

    except:
        return "-"


# ================= GEO =================
def get_lat_lon(city, df=pd.DataFrame()):

    if not df.empty:
        df_city = df[df['city'].str.lower() == city.lower()]

        if not df_city.empty:
            return (
                df_city.iloc[-1]['lat'],
                df_city.iloc[-1]['lon']
            )

    url = "https://geocoding-api.open-meteo.com/v1/search"

    try:
        response = requests.get(
            url,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            return (
                round(data['results'][0]['latitude'], 2),
                round(data['results'][0]['longitude'], 2)
            )

        return -6.45, 106.14

    except:
        return -6.45, 106.14


# ================= HISTORY =================
def get_7_days_history_api(lat, lon):

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&past_days=7"
        f"&forecast_days=0"
        f"&daily=temperature_2m_mean,precipitation_sum"
        f"&timezone=Asia%2FJakarta"
    )

    try:
        data = requests.get(url, timeout=5).json()

        dates = data['daily']['time']
        temps = data['daily']['temperature_2m_mean']
        rains = data['daily']['precipitation_sum']

        history = []

        for i in range(7):

            dt_obj = datetime.strptime(dates[i], "%Y-%m-%d")

            history.append({
                "date": dt_obj.strftime("%d %b"),
                "day": dt_obj.strftime("%a"),
                "temp": round(temps[i], 1),
                "rain": round(rains[i], 1),
                "icon": get_icon_day(temps[i], rains[i])
            })

        return history

    except Exception as e:
        print("Gagal fetch histori:", e)
        return []


# ================= CURRENT WEATHER =================
def get_current(city, lat=None, lon=None):

    if lat is None or lon is None:
        lat, lon = get_lat_lon(city)

    if not WEATHER_API_KEY:
        return None

    url = "https://api.weatherapi.com/v1/forecast.json"

    try:
        response = requests.get(
            url,
            params={"key": WEATHER_API_KEY, "q": f"{lat},{lon}", "days": 1, "aqi": "no"},
            timeout=8,
        )
        response.raise_for_status()
        d = response.json()

        now_hour = datetime.now(jakarta_tz).hour

        current_chance = d['forecast']['forecastday'][0]['hour'][now_hour]['chance_of_rain']

        wind_degree = d['current']['wind_degree']

        return {
            "temp": d['current']['temp_c'],
            "humidity": d['current']['humidity'],
            "desc": d['current']['condition']['text'],
            "wind": d['current']['wind_kph'],
            "wind_dir": wind_degree,
            "wind_dir_text": get_wind_direction_text(wind_degree),
            "pressure": d['current']['pressure_mb'],
            "feels": d['current']['feelslike_c'],
            "rain": d['current']['precip_mm'],
            "chance_of_rain": current_chance,
            "uv": d['current']['uv']
        }

    except Exception as e:
        print("ERROR CURRENT:", e)
        return None


# ================= HOURLY =================
def get_hourly(lat, lon):

    if not WEATHER_API_KEY:
        return []

    url = "https://api.weatherapi.com/v1/forecast.json"

    try:
        response = requests.get(
            url,
            params={"key": WEATHER_API_KEY, "q": f"{lat},{lon}", "days": 1, "aqi": "no"},
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        res = []

        now_hour = datetime.now(jakarta_tz).hour

        hours_data = data['forecast']['forecastday'][0]['hour']

        for item in hours_data[now_hour:now_hour+8]:

            res.append({
                "time": item['time'][11:16],
                "temp": round(item['temp_c']),
                "hum": item['humidity'],
                "icon": get_icon(item['condition']['text'])
            })

        return res

    except:
        return []


# ================= 3 HOURLY =================
def get_3_hourly(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,weathercode"
        f"&timezone=Asia%2FJakarta"
        f"&forecast_days=2"
    )

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        if 'error' in data or 'hourly' not in data:
            return []

        times = data['hourly'].get('time', [])
        temps = data['hourly'].get('temperature_2m', [])
        hums = data['hourly'].get('relative_humidity_2m', [])
        rains = data['hourly'].get('precipitation', [])
        wmo_codes = data['hourly'].get('weathercode', [])
        if not times:
            return []

        def map_icon(code, hour):
            if code is not None:
                if 51 <= code <= 67 or 80 <= code <= 82:
                    return "bi-cloud-rain-fill"
                if code >= 95:
                    return "bi-cloud-lightning-rain-fill"
            is_night = hour >= 18 or hour < 6
            if code is not None and code <= 1:
                return "bi-moon-stars-fill" if is_night else "bi-sun-fill"
            if code is not None and code <= 3:
                return "bi-cloud-moon-fill" if is_night else "bi-cloud-fill"
            return "bi-cloud-moon-fill" if is_night else "bi-cloud-fill"

        now_hour = datetime.now(jakarta_tz).hour
        result = []
        for i in range(now_hour, min(now_hour + 24, len(times)), 3):
            hour = int(times[i][11:13])
            result.append({
                "time": times[i][-5:],
                "temp": round(temps[i]),
                "hum": hums[i],
                "rain": round(rains[i], 1),
                "icon": map_icon(wmo_codes[i], hour),
            })
        return result
    except Exception as exc:
        print("ERROR 3 HOURLY:", exc)
        return []


# ================= RECENT HOURLY =================
def get_recent_hourly(lat, lon):

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&past_days=1"
        f"&forecast_days=1"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        f"&timezone=Asia%2FJakarta"
    )

    try:
        data = requests.get(url, timeout=5).json()

        times = data['hourly']['time']
        temps = data['hourly']['temperature_2m']
        hums = data['hourly']['relative_humidity_2m']
        winds = data['hourly']['wind_speed_10m']

        now = datetime.now(jakarta_tz)

        current_hour_str = now.strftime("%Y-%m-%dT%H:00")

        try:
            current_idx = times.index(current_hour_str)

        except ValueError:
            current_idx = len(times) // 2

        start_idx = max(0, current_idx - 12)
        end_idx = current_idx + 1

        labels_rt = []
        temps_rt = []
        hums_rt = []
        winds_rt = []

        for i in range(start_idx, end_idx):

            dt_obj = datetime.strptime(
                times[i],
                "%Y-%m-%dT%H:%M"
            )

            labels_rt.append(dt_obj.strftime("%H:%M"))
            temps_rt.append(temps[i])
            hums_rt.append(hums[i])
            winds_rt.append(winds[i])

        return labels_rt, temps_rt, hums_rt, winds_rt

    except Exception as e:
        print("ERROR RECENT:", e)
        return [], [], [], []


# ================= DATA PROCESSING =================
def read_data():

    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()

    df = pd.read_csv(CSV_PATH, sep=None, engine='python')

    df.columns = df.columns.str.strip().str.lower()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df = df.dropna(subset=['date'])

    num_cols = [
        'temperature_2m_mean',
        'precipitation_sum',
        'windspeed_10m_max',
        'cape_proxy_radiation',
        'lat',
        'lon'
    ]

    for col in num_cols:

        if col in df.columns:

            df[col] = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df.sort_values(['city', 'date'])


def calculate_extra_features(df):

    if df.empty or 'date' not in df.columns:
        return df

    df = df.copy()

    df['date'] = pd.to_datetime(df['date'])

    df['month'] = df['date'].dt.month
    df['tahun_ke'] = df['date'].dt.year
    df['day_of_year'] = df['date'].dt.dayofyear

    df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
    df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)

    df['sin_day'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
    df['cos_day'] = np.cos(2 * np.pi * df['day_of_year'] / 365)

    df['sst_anomaly'] = np.sin(df['month'] * np.pi / 6) * 1.5
    df['enso_index'] = np.sin((df['tahun_ke'] - 2019) * np.pi / 1.5) * 2.0
    df['iod_index'] = np.cos(df['month'] * np.pi / 6) * 1.2

    df['temp_lag1'] = df.groupby('city')['temperature_2m_mean'].shift(1)
    df['temp_lag2'] = df.groupby('city')['temperature_2m_mean'].shift(2)

    df['rain_lag1'] = df.groupby('city')['precipitation_sum'].shift(1)

    df['temp_roll3'] = (
        df.groupby('city')['temperature_2m_mean']
        .rolling(3)
        .mean()
        .reset_index(0, drop=True)
    )

    df['rain_roll3'] = (
        df.groupby('city')['precipitation_sum']
        .rolling(3)
        .mean()
        .reset_index(0, drop=True)
    )

    df['temp_diff'] = (
        df.groupby('city')['temperature_2m_mean']
        .diff()
    )

    df['rain_diff'] = (
        df.groupby('city')['precipitation_sum']
        .diff()
    )

    return df.dropna()


# ================= CNN-LSTM =================
def predict_ai(df, lat, lon, current_weather=None):

    model, bundle = load_ai()

    df = df.copy()

    df['distance'] = np.sqrt(
        (df['lat'] - lat)**2 +
        (df['lon'] - lon)**2
    )

    df_city = (
        df.sort_values('distance')
        .head(500)
        .sort_values('date')
    )

    if len(df_city) < TIME_STEPS:
        df_city = df.sort_values('date').tail(TIME_STEPS + 50)

    seq_raw = df_city[FEATURES].tail(TIME_STEPS).copy()

    if seq_raw.shape[0] < TIME_STEPS:
        return [(28.0, 0.0)] * 7

    scaler_X = bundle['scaler_X']
    scaler_y = bundle['scaler_y']

    seq_scaled = scaler_X.transform(seq_raw)

    result = []

    for i in range(7):

        pred = model.predict(
            seq_scaled.reshape(1, TIME_STEPS, len(FEATURES)),
            verbose=0
        )[0]

        inversed = scaler_y.inverse_transform(
            [[pred[0], pred[1]]]
        )[0]

        temp = inversed[0]
        rain_val = inversed[1]

        rain = np.expm1(rain_val)

        if i == 0 and current_weather:

            live_rain = float(current_weather.get('rain', 0))
            live_hum = float(current_weather.get('humidity', 0))

            if live_hum > 85 and live_rain > 5:
                rain = (rain * 0.3) + (live_rain * 0.7)

            else:
                rain = (rain * 0.7) + (live_rain * 0.3)

        if rain < 0.1:
            rain = 0.0

        temp_final = round(float(temp), 1)
        rain_final = round(float(rain), 1)

        result.append((temp_final, rain_final))

        new_row = seq_raw.iloc[-1].copy()

        new_row['temperature_2m_mean'] = temp_final
        new_row['precipitation_sum'] = rain_final

        seq_raw = pd.concat([
            seq_raw.iloc[1:],
            pd.DataFrame([new_row])
        ])

        seq_scaled = scaler_X.transform(seq_raw)

    return result


# ================= DASHBOARD =================
def weather_view(request):

    city = request.POST.get("city", "Banten")

    now = datetime.now(jakarta_tz)

    df_raw = read_data()

    lat, lon = get_lat_lon(city, df_raw)

    weather = get_current(city, lat, lon)

    if weather and not df_raw.empty:

        api_row = {
            'city': city,
            'date': now.replace(tzinfo=None),
            'temperature_2m_mean': float(weather['temp']),
            'precipitation_sum': float(weather.get('rain', 0)),
            'windspeed_10m_max': float(weather['wind']),
            'cape_proxy_radiation': float(weather.get('uv', 5.0) * 100),
            'lat': float(lat),
            'lon': float(lon)
        }

        df_raw = pd.concat(
            [df_raw, pd.DataFrame([api_row])],
            ignore_index=True
        )

    df = calculate_extra_features(df_raw)

    prediction_source = "CNN-LSTM"
    prediction_error = None
    try:
        future = predict_ai(df, lat, lon, weather)
    except Exception as exc:
        # Keep the dashboard available even when the model runtime or artifact is unavailable.
        print("CNN-LSTM prediction failed:", exc)
        prediction_source = "Historical baseline"
        prediction_error = "Model AI belum dapat dimuat. Prediksi sementara menggunakan data historis."
        if not df.empty and {"temperature_2m_mean", "precipitation_sum"}.issubset(df.columns):
            baseline = df[["temperature_2m_mean", "precipitation_sum"]].tail(7).mean()
            future = [(round(float(baseline.iloc[0]), 1), round(max(float(baseline.iloc[1]), 0.0), 1))] * 7
        else:
            future = [(28.0, 0.0)] * 7

    map_cities = [
        "Serang",
        "Cilegon",
        "Tangerang",
        "Tangerang Selatan",
        "Pandeglang",
        "Rangkasbitung"
    ]

    city_weather_data = {}

    for c in map_cities:

        if c.lower() == city.lower() and weather:
            city_weather_data[c] = weather

        else:
            c_lat, c_lon = get_lat_lon(c, df_raw)

            w_data = get_current(c, c_lat, c_lon)

            if w_data:
                city_weather_data[c] = w_data

    history = get_7_days_history_api(lat, lon)

    if not history:

        history_data = df[
            df['city'].str.lower() == city.lower()
        ]

        if history_data.empty:
            history_data = df[
                df['city'].str.lower() == 'serang'
            ]

        if history_data.empty:
            history_data = df

        history_data = history_data[
            history_data['date'].dt.date < now.date()
        ].tail(7)

        for _, r in history_data.iterrows():

            history.append({
                "date": r['date'].strftime("%d %b"),
                "day": r['date'].strftime("%a"),
                "temp": float(round(r['temperature_2m_mean'], 1)),
                "rain": float(round(r['precipitation_sum'], 1)),
                "icon": get_icon_day(
                    r['temperature_2m_mean'],
                    r['precipitation_sum']
                )
            })

    forecast = []

    for i in range(len(future)):

        t, r = future[i]

        dt = now + timedelta(days=i)

        forecast.append({
            "date": dt.strftime("%d %b"),
            "day": dt.strftime("%a"),
            "temp": t,
            "rain": r,
            "icon": get_icon_day(t, r)
        })

    labels = (
        [h['date'] for h in history] +
        [f['date'] for f in forecast]
    )

    chart_hist = (
        [h['temp'] for h in history] +
        [None] * len(forecast)
    )

    if len(history) > 0:

        chart_pred = (
            [None] * (len(history)-1) +
            [history[-1]['temp']] +
            [f['temp'] for f in forecast]
        )

    else:
        chart_pred = [f['temp'] for f in forecast]

    chart_rain = (
        [h['rain'] for h in history] +
        [f['rain'] for f in forecast]
    )

    context = {
        "city": city,
        "current": weather,
        "prediction_source": prediction_source,
        "prediction_error": prediction_error,
        "hourly": get_hourly(lat, lon),
        "history": history,
        "forecast": forecast,
        "city_weather_json": city_weather_data,
        "chart_labels": labels,
        "chart_hist": chart_hist,
        "chart_pred": chart_pred,
        "chart_rain": chart_rain,
        "forecast_rain_values": [item["rain"] for item in forecast]
    }

    return render(request, "weather.html", context)


# ================= API =================
def weather_api(request):

    city = request.GET.get("city", "Banten")

    lat, lon = get_lat_lon(city)

    weather = get_current(city, lat, lon)

    if weather:

        return JsonResponse({
            "temp": float(weather['temp']),
            "wind": float(weather['wind']),
            "hum": int(weather['humidity']),
            "wind_dir": weather['wind_dir'],
            "wind_dir_text": weather['wind_dir_text'],
            "success": True
        })

    return JsonResponse({"success": False}, status=400)


# ================= DETAIL VIEW =================
def city_detail_view(request, city):

    lat, lon = get_lat_lon(city)

    weather = get_current(city, lat, lon)

    labels_rt, temps_rt, hums_rt, winds_rt = get_recent_hourly(lat, lon)

    forecast_3h = get_3_hourly(lat, lon)

    context = {
        "city": city,
        "current": weather,
        "forecast_3h": forecast_3h,
        "labels_json": json.dumps(labels_rt),
        "temps_json": json.dumps(temps_rt),
        "hums_json": json.dumps(hums_rt),
        "winds_json": json.dumps(winds_rt),
    }

    return render(request, "weather_detail.html", context)