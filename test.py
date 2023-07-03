import app

class TestFlaskWeatherApp:
    def setup_method(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def test_index(self):
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data

    def test_get_weather(self):
        response = self.client.get('/weather?city=London')
        assert response.status_code == 200
        data = response.json
        assert 'weather' in data
        assert 'forecast' in data
        assert 'advice' in data

    def test_get_weather_without_city(self):
        response = self.client.get('/weather')
        assert response.status_code == 400
        data = response.json
        assert data['error'] == 'City parameter is required.'

