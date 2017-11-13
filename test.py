import settings
import requests

geotag = (40.671997, -73.957407)
office = (40.739527, -73.994145)
url = 'https://maps.googleapis.com/maps/api/directions/json?origin={},{}&destination={},{}&mode=transit&key={}'.format(geotag[0], geotag[1], office[0], office[1], settings.DIRECTIONS_API_KEY)
    
response = requests.get(url)
print(response.json()["routes"][0]["legs"][0]["duration"]["value"])