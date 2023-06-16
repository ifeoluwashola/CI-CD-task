import unittest
import app

class FlaskWeatherAppTestCase(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_get_weather(self):
        response = self.client.get('/weather?city=London')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue('weather' in data)
        self.assertTrue('forecast' in data)
        self.assertTrue('advice' in data)

    def test_get_weather_without_city(self):
        response = self.client.get('/weather')
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertEqual(data['error'], 'City parameter is required.')

if __name__ == '__main__':
    unittest.main()

