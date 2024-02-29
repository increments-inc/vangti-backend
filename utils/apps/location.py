import polyline
from django.conf import settings
import requests
# from django.contrib.gis.measure import D, Distance
from locations.models import PolyLine, UserLocation
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis.db.models.functions import Distance

def get_user_distance(from_user, to_user):
    to_point = UserLocation.objects.get(user=to_user.id).centre
    distance = (
        UserLocation.objects.filter(user=from_user.id).annotate(
            distance=Distance("centre", to_point)
        ).values("distance").first()["distance"].km
    )
    return distance

def polyline_to_latlong(poly_str):
    res = polyline.decode(poly_str, 5)
    # print("decoded polyline   ", res)

    return res


def latlong_to_address(latlong):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlong}&key={settings.GOOGLE_MAPS_API_KEY}"
    re_geo_response = requests.request("GET", url)
    try:
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
    # transaction_id=787
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
    if poly_obj.linestring is not None:

        source_deviation = PolyLine.objects.filter(transaction=transaction_id).annotate(
            distance=Distance("linestring", source_point)).values(
            "linestring", "distance").values("distance").first()["distance"].km
        destination_deviation = PolyLine.objects.filter(transaction=transaction_id).annotate(
            distance=Distance("linestring", destination_point)).values(
            "linestring", "distance").values("distance").first()["distance"].km

        # if source_deviation < 30 and destination_deviation < 30:
        #     return poly_obj.linestring

    if (poly_obj.linestring is None) or (source_deviation > 3000000 or destination_deviation > 3000000):
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
            # "distance": response["routes"][0]["legs"][0]["distance"]["text"],
            # "duration": response["routes"][0]["legs"][0]["duration"]["text"],
            "distance": "less ",
            "duration": "ajsdhah",
            "polyline": empty_point_list
        }
    else:
        ls = poly_obj.linestring
        # source cut
        source_point_in_ls = ls.interpolate(ls.project(source_point))
        new_source_point = Point(source_point_in_ls.y, source_point_in_ls.x, srid=4326)
        new_scoords = ls.coords.index(tuple(source_point_in_ls))
        print("new  cosjdhfjsdhf", new_scoords, new_source_point)
        # destination cut
        destination_point_in_ls = ls.interpolate(ls.project(destination_point))
        new_destination_point = Point(destination_point_in_ls.y, destination_point_in_ls.x, srid=4326)
        new_dcoords = ls.coords.index(tuple(destination_point_in_ls))
        print("new  cosjdhfjsdhf", new_dcoords, new_destination_point)
        list_ls = []
        if new_dcoords>new_scoords:
            list_ls = ls[new_scoords: new_dcoords+1]
            list_ls.insert(0, new_source_point)
            list_ls.append(new_destination_point)
        if new_dcoords<new_scoords:
            list_ls = ls[new_dcoords: new_scoords+1]
            list_ls.insert(0, new_destination_point)
            list_ls.append(new_source_point)
        if new_dcoords==new_scoords:
            list_ls = ls
        empty_point_list = []
        for point in list_ls:
            empty_point_list.append({
                "latitude": point[0],
                "longitude": point[1]
            })
        response_json = {
            "distance": "hajgsdjm",
            "duration": "ajsdhah",
            "polyline": empty_point_list
        }



    return response_json

