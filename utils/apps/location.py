import polyline
from django.conf import settings
import requests


def polyline_to_latlong(poly_str):
    res = polyline.decode(poly_str, 5)
    # print("decoded polyline   ", res)
    return res


def latlong_to_address(latlong):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlong}&key={settings.GOOGLE_MAPS_API_KEY}"
    re_geo_response = requests.request("GET", url)
    try:
        print("reverse geocoding \n", re_geo_response.json())
        formatted_address = re_geo_response.json()["results"][0]["formatted_address"]
        place_id = re_geo_response.json()["results"][0]["place_id"]
    except:
        formatted_address = re_geo_response.json()["results"][0]["formatted_address"]
        place_id = re_geo_response.json()["results"][0]["place_id"]
    return {
            "formatted_address": formatted_address,
            "place_id": place_id
        }


def get_directions(source, destination):
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={settings.GOOGLE_MAPS_API_KEY}&mode=walking"
    direction_response = requests.request("GET", directions_url)
    try:
        print("reverse geocoding \n", direction_response.json())
        response_json = direction_response.json()
    except:
        response_json = ""
    return response_json



"""
{
                "start_location": 0.0,
                "end_location": 0.0,
                "distance": "0 km",
                "duration": "0 min",
                "polyline": [(0, 0)]
            }
"""
