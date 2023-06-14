import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/weather')
def get_weather():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    api_key = os.getenv('API_KEY')  

    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric'
    response = requests.get(url)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch weather data.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

