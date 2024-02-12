import polyline
from django.conf import settings
import requests
# from django.contrib.gis.measure import D, Distance
from locations.models import PolyLine
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis.db.models.functions import Distance


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


# def get_polyline_object(transaction_id, source_point, destination_point):
#     print("hdjhajsda")
#     poly = PolyLine.objects.filter(transaction=transaction_id)
#     print(poly.count())
#     if poly.exists():
#         poly_obj = poly.first()
#     else:
#         poly_obj = PolyLine.objects.create(
#             transaction=transaction_id
#         )
#     print("in here")
#     if poly_obj.linestring is not None:
#         source_deviation = PolyLine.objects.filter(transaction=transaction_id).annotate(
#             distance=Distance("linestring", source_point)).values(
#             "linestring", "distance")
#         destination_deviation = PolyLine.objects.filter(transaction=transaction_id).annotate(
#             distance=Distance("linestring", destination_point)).values(
#             "linestring", "distance")
#         if source_deviation < 30 and destination_deviation < 30:
#             return poly_obj.linestring
#         else:
#             return -1
#     return None


def get_directions(transaction_id, source_dict, destination_dict):
    response_json={}
    print(source_dict, destination_dict, transaction_id)
    source = f"{source_dict['latitude']}, {source_dict['longitude']}"
    destination = f"{destination_dict['latitude']}, {destination_dict['longitude']}"
    # ls = get_polyline_object(
    #     transaction_id,
    #     Point(source_dict['longitude'], source_dict['latitude'], srid=4326),
    #     Point(destination_dict['longitude'], destination_dict['latitude'], srid=4326),
    # )
    source_deviation = destination_deviation = 0
    source_point = Point(source_dict['longitude'], source_dict['latitude'], srid=4326)
    destination_point = Point(destination_dict['longitude'], destination_dict['latitude'], srid=4326)
    poly = PolyLine.objects.filter(transaction=transaction_id)
    if poly.exists():
        poly_obj = poly.first()
    else:
        poly_obj = PolyLine.objects.create(
            transaction=transaction_id
        )
    print("here fsdfs", "poly_obj.linestring")
    if poly_obj.linestring is not None:

        source_deviation = PolyLine.objects.filter(transaction=transaction_id).annotate(
            distance=Distance("linestring", source_point)).values(
            "linestring", "distance").values("distance").first()["distance"].km
        destination_deviation = PolyLine.objects.filter(transaction=transaction_id).annotate(
            distance=Distance("linestring", destination_point)).values(
            "linestring", "distance").values("distance").first()["distance"].km
        print("im here in no tnone", type(source_deviation), destination_deviation)

        # if source_deviation < 30 and destination_deviation < 30:
        #     return poly_obj.linestring

    if (poly_obj.linestring is None) or (source_deviation > 300 or destination_deviation > 300):
        directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={settings.GOOGLE_MAPS_API_KEY}&mode=walking"
        direction_response = requests.request("GET", directions_url)
        # direction_response ={}

        # try:
        response = direction_response.json()
        print("direction \n", direction_response.json())

        polyline = response['routes'][0]['overview_polyline']["points"]
        polyline_points = polyline_to_latlong(polyline)
        poly_obj.linestring = LineString(polyline_points)
        poly_obj.save()
        empty_point_list = []
        for point in polyline_points:
            empty_point_list.append({
                "latitude": point[0],
                "longitude": point[1]
            })
        response_json = {
            "distance": response["routes"][0]["legs"]["distance"]["text"],
            "duration": response["routes"][0]["legs"]["duration"]["text"],
            "polyline": empty_point_list
        }
    else:
        print("i am here")
        ls = poly_obj.linestring
        empty_point_list = []
        for point in ls:
            empty_point_list.append({
                "latitude": point[1],
                "longitude": point[0]
            })
        response_json = {
            "distance": "hajgsdjm",
            "duration": "ajsdhah",
            "polyline": empty_point_list
        }


        # except:
        #     response_json = {
        #         "distance": "0 km",
        #         "duration": "0 min",
        #         "polyline": [
        #             {
        #                 "latitude": 0.0,
        #                 "longitude": 0.0
        #             }
        #         ]
        #     }
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
