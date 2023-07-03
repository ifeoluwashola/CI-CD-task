from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta
from prometheus_flask_exporter import PrometheusMetrics
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# OpenWeatherMap API endpoints
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Retrieve OpenWeatherMap API key from environment variable
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

# Configure logging
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)  # Set global log level to DEBUG

@app.route('/')
def index():
    request_method = request.method
    user_agent = request.headers.get('User-Agent')
    log_message = f"Successful request for '/'. Method: {request_method}, From: {request.remote_addr}, At: {datetime.now()}, User-Agent: {user_agent}"
    app.logger.debug(log_message)
    return open('static/index.html').read()

@app.route('/weather')
def get_weather():
    city = request.args.get('city', '')
    request_method = request.method
    user_agent = request.headers.get('User-Agent')
    log_message = f"Successful request for '/weather'. Method: {request_method}, City: {city}, From: {request.remote_addr}, At: {datetime.now()}, User-Agent: {user_agent}"
    app.logger.debug(log_message)

    if not city:
        error_message = 'City parameter is required.'
        app.logger.error(error_message)
        return jsonify({'error': error_message}), 400

    params = {
        'q': city,
        'units': 'metric',
        'appid': WEATHER_API_KEY,
    }

    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()

    if response.status_code != 200:
        error_message = f"Failed to retrieve weather data. Error: {data.get('message', 'Unknown error')}, Status code: {response.status_code}"
        app.logger.error(error_message)
        return jsonify({'error': error_message}), 500

    # Extract relevant weather data from the current weather API response
    current_weather = {
        'temperature': data['main']['temp'],
        'condition': data['weather'][0]['description'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'sunrise': format_timestamp(data['sys']['sunrise']),
        'sunset': format_timestamp(data['sys']['sunset']),
        'country': data['sys']['country'],
        'visibility': data['visibility'],
        'weather_icon': f"http://openweathermap.org/img/w/{data['weather'][0]['icon']}.png"
    }

    # Get weather forecast for today and the next two days
    forecast = get_weather_forecast(city)

    # Provide advice based on weather conditions
    advice = get_weather_advice(current_weather)

    # Log successful response and request details
    log_message = f"Successful response for '/weather' from {request.remote_addr} at {datetime.now()}. City: {city}"
    app.logger.info(log_message)

    return jsonify({
        'weather': current_weather,
        'forecast': forecast,
        'advice': advice
    })

def get_weather_forecast(city):
    params = {
        'q': city,
        'units': 'metric',
        'appid': WEATHER_API_KEY,
    }

    response = requests.get(FORECAST_API_URL, params=params)
    data = response.json()

    if response.status_code != 200:
        error_message = 'Failed to retrieve weather forecast'
        app.logger.error(error_message)
        return None

    forecast = []

    # Tomorrow's weather
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_weather = {
        'date': tomorrow.strftime('%Y-%m-%d'),
        'temperature': data['list'][1]['main']['temp'],
        'condition': data['list'][1]['weather'][0]['description']
    }
    forecast.append(tomorrow_weather)

    # Next day's weather
    next_day = datetime.now() + timedelta(days=2)
    next_day_weather = {
        'date': next_day.strftime('%Y-%m-%d'),
        'temperature': data['list'][2]['main']['temp'],
        'condition': data['list'][2]['weather'][0]['description']
    }
    forecast.append(next_day_weather)

    # Next 2 day's weather
    next_2_day = datetime.now() + timedelta(days=3)
    next_2_day_weather = {
        'date': next_2_day.strftime('%Y-%m-%d'),
        'temperature': data['list'][3]['main']['temp'],
        'condition': data['list'][3]['weather'][0]['description']
    }
    forecast.append(next_2_day_weather)

    return forecast

def get_weather_advice(current_weather):
    temperature = current_weather['temperature']
    condition = current_weather['condition']

    # Provide advice based on weather conditions and temperature
    if 'rain' in condition.lower():
        advice = "It's currently raining. Don't forget to take an umbrella!"
    elif 'snow' in condition.lower():
        advice = "It's currently snowing. Bundle up and stay warm!"
    elif 'clear' in condition.lower():
        advice = "It's a clear day. Enjoy the sunshine!"
    elif 'cloud' in condition.lower():
        advice = "It's cloudy outside. Take a jacket just in case."
    elif temperature < 10:
        advice = "It's cold outside. Dress warmly!"
    elif temperature > 25:
        advice = "It's hot outside. Stay hydrated!"
    else:
        advice = "Enjoy the weather!"

    return advice

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

