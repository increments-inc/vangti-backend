import polyline
from django.conf import settings
import requests
from django.contrib.gis.measure import D, Distance
# from django.contrib.gis.db.models.functions import Distance
from locations.models import PolyLine
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis.geos import GEOSGeometry

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


def get_polyline_object(transaction_id, source_point, destination_point):
    poly = PolyLine.objects.filter(transaction_id=transaction_id)
    if poly.exists():
        poly_obj = poly.first()
    else:
        poly_obj = PolyLine.objects.create(
            transaction_id=transaction_id
        )

    if poly_obj.linestring is not None:
        source_deviation = PolyLine.objects.filter(transaction_id=transaction_id).annotate(
            distance=Distance("linestring", source_point)).values(
            "linestring", "distance")
        destination_deviation = PolyLine.objects.filter(transaction_id=transaction_id).annotate(
            distance=Distance("linestring", destination_point)).values(
            "linestring", "distance")
        if source_deviation < 30 and destination_deviation < 30:
            return poly_obj.linestring
        else:
            return -1
    return None


def get_directions(transaction_id, source, destination):
    print(source, destination, transaction_id)
    source = f"{source['latitude']}, {source['longitude']}"
    destination = f"{destination['latitude']}, {destination['longitude']}"
    ls = get_polyline_object(
        transaction_id,
        Point(source['longitude'], source['latitude'], srid=4326),
        Point(destination['longitude'], destination['latitude'], srid=4326),
    )


    if ls ==-1:
        directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={settings.GOOGLE_MAPS_API_KEY}&mode=walking"
        # direction_response = requests.request("GET", directions_url)
        direction_response ={}
        try:
            print("direction \n", direction_response.json())
            response = direction_response.json()
            response_json = {
                "distance": "",
                "duration": "0 min",
                "polyline": [
                    {
                        "latitude": 0.0,
                        "longitude": 0.0
                    },
                    {
                        "latitude": 0.0,
                        "longitude": 0.0
                    }
                ]
            }


        except:
            response_json = {
                "distance": "0 km",
                "duration": "0 min",
                "polyline": [
                    {
                        "latitude": 0.0,
                        "longitude": 0.0
                    },
                    {
                        "latitude": 0.0,
                        "longitude": 0.0
                    }
                ]
            }
    return response_json


def process_polyline():
    empty_array = []
    array = polyline_to_latlong(
        'y{upCemufP}@?AWP?rACnDClFE|JGvA?CiB?kBAsACeGnJ?t@ETGLKNAtABnB?hECnEItB?jHMdBAZ}EtAqTB}@@Q')
    for arr in array:
        empty_array.append(Point(arr[1], arr[0]))
    point = Point(90, 23)

    pl = PolyLine.objects.create(
        linestring=LineString(empty_array),
        point=point
    )
    pl = PolyLine.objects.filter()
    print(pl)
    distance = 5
    # print(PolyLine.objects.filter(
    #     linestring__ST_DWithin(point, D(m=5))
    # )
    # )

# process_polyline()
# polyline_to_latlong(
#         'y{upCemufP}@?AWP?rACnDClFE|JGvA?CiB?kBAsACeGnJ?t@ETGLKNAtABnB?hECnEItB?jHMdBAZ}EtAqTB}@@Q')