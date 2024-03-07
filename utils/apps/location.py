import polyline
from django.conf import settings
import requests
from django.contrib.gis.measure import D
from locations.models import PolyLine, UserLocation
from django.contrib.gis.geos import Point, LineString, WKTWriter
from django.contrib.gis.db.models.functions import Distance
from users.models import User
import math
from decimal import Decimal
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
import re

def get_user_location(user_id):
    return UserLocation.objects.get(user=user_id).centre


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


def get_nearby_users(user_id):
    center = UserLocation.objects.using('location').get(user=user_id).centre
    radius = settings.LOCATION_RADIUS
    return list(
        UserLocation.objects.using('location').filter(
            centre__distance_lte=(center, D(km=radius))
        ).annotate(
            distance=Distance('centre', center)
        ).order_by(
            'distance'
        ).values_list(
            "user", flat=True
        )
    )


# def get_user_list(user):
#     user_location_list = get_nearby_users(user.id)
#     user_provider_list = list(
#         User.objects.filter(
#             is_superuser=False,
#             id__in=user_location_list,
#             user_mode__is_provider=True
#         ).values_list(
#             'id', flat=True
#         )
#     )
#     user_list = [str(id) for id in user_provider_list]
#     return user_list

def get_user_list_provider(user):
    user_location_list = get_nearby_users(user.id)
    user_provider_list = (
        User.objects.filter(
            is_superuser=False,
            id__in=user_location_list,
            user_mode__is_provider=True
        )
    )

    return user_provider_list


def get_user_list_seeker(user):
    user_location_list = get_nearby_users(user.id)
    user_provider_list = (
        User.objects.filter(
            is_superuser=False,
            id__in=user_location_list,
            user_mode__is_provider=False
        )
    )

    return user_provider_list


def get_user_list(user):
    user_location_list = get_nearby_users(user.id)
    user_list = (
        User.objects.filter(
            is_superuser=False,
            id__in=user_location_list,
            # user_mode__is_provider=False
        )
    )

    return user_list


def get_user_id_list(user):
    user_location_list = get_nearby_users(user.id)
    user_provider_list = list(
        User.objects.filter(
            is_superuser=False,
            id__in=user_location_list,
            user_mode__is_provider=True
        ).values_list(
            'id', flat=True
        )
    )
    final_user_list = []
    for user in user_location_list:
        if user in user_provider_list:
            final_user_list.append(user)

    user_list = [str(id) for id in final_user_list]
    return user_list


def rounding(number):
    decimal_number = Decimal(str(number))  # Convert to Decimal
    cut_number = decimal_number.quantize(Decimal('0.' + '0' * (5 - 1) + '1'))  # Precision of 5 decimal places
    return float(cut_number)

def degress_to_meters(number):
    m = round((
        number *
         2 * math.pi * 6378.137
         / 360
         * 1000), 3
    )
    return m

def segment_polyline(line_string, point):
    cursor = connection.cursor()
    print("here")
    cursor.execute(
        f"""WITH data AS (SELECT '{line_string}'::geometry AS line, '{point}':: geometry AS point) SELECT ST_AsText( ST_Split( ST_Snap(line, point, 1), point)) AS snapped_split, ST_AsText( ST_Split(line, point)) AS not_snapped_not_split FROM data;"""
        # f"""WITH data AS (SELECT '{line_string}'::geometry AS line,'{point}'::geometry AS point),split_data AS (SELECT ST_Split(ST_Snap(line, point, 1), point) AS snapped_split,ST_Split(line, point) AS not_snapped_not_split FROM data) SELECT ST_AsText(ST_CollectionExtract(snapped_split, 2)) AS snapped_split, ST_AsText(ST_CollectionExtract(not_snapped_not_split, 2)) AS not_snapped_not_split FROM split_data;"""
    )
    split_geom = cursor.fetchone()
    print(split_geom)
    return split_geom


def call_maps_api(source, destination):
    # directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={settings.GOOGLE_MAPS_API_KEY}&mode=walking"
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={settings.GOOGLE_MAPS_API_KEY}"
    direction_response = requests.request("GET", directions_url)
    response = direction_response.json()
    print("DIRECTION API CALLED !!! \n", )

    return {
        "distance": response["routes"][0]["legs"][0]["distance"]["text"],
        "duration": response["routes"][0]["legs"][0]["duration"]["text"],
        "polyline": response['routes'][0]['overview_polyline']["points"]
    }

"""
def get_directions0(transaction_id, source_dict, destination_dict):
    # transaction_id = 787
    # into coordinate strings for api call
    source = f"{source_dict['latitude']}, {source_dict['longitude']}"
    destination = f"{destination_dict['latitude']}, {destination_dict['longitude']}"

    # initial deviation
    source_deviation = destination_deviation = 0

    # source and destination points
    source_point = Point(source_dict['latitude'], source_dict['longitude'], srid=4326)
    destination_point = Point(destination_dict['latitude'], destination_dict['longitude'], srid=4326)

    poly = PolyLine.objects.filter(transaction=transaction_id)
    if poly.exists():
        poly_obj = poly.first()
    else:
        poly_obj = PolyLine.objects.create(
            transaction=transaction_id,
            seeker_location=Point(source_dict['longitude'], source_dict['latitude'], srid=4326),
            provider_location=Point(destination_dict['longitude'], destination_dict['latitude'], srid=4326)
        )

    # polyline was previously created
    if poly_obj.linestring is not None:
        # source deviation
        source_deviation = PolyLine.objects.filter(
            transaction=transaction_id
        ).annotate(
            distance=Distance("linestring", source_point)
        ).values("distance").first()["distance"].km

        destination_deviation = PolyLine.objects.filter(
            transaction=transaction_id
        ).annotate(
            distance=Distance("linestring", destination_point)
        ).values("distance").first()["distance"].km

    # if polyline line string newly created or there is significant deviation
    if (
            poly_obj.linestring is None or
            source_deviation > 5 or
            destination_deviation > 5
    ):
        direction_response = call_maps_api(source, destination)
        polyline_points = polyline_to_latlong(direction_response["polyline"])
        poly_obj.linestring = LineString(polyline_points)
        poly_obj.save()

        polyline_points_list = []
        for point in polyline_points:
            polyline_points_list.append({
                "latitude": point[0],
                "longitude": point[1]
            })

        return {
            "distance": direction_response["distance"],
            "duration": direction_response["duration"],
            "polyline": polyline_points_list
        }

    # polyline cut
    ls = poly_obj.linestring
    print("linestring print", ls)


    # source cut
    interpolated_source_point = ls.interpolate(ls.project(source_point))

    # interpolated_source_point = WKTWriter(precision=5).write(interpolated_source_point)
    interpolated_destination_point = ls.interpolate(ls.project(destination_point))
    # interpolated_destination_point = WKTWriter(precision=5).write(interpolated_destination_point)

    # interpolated_source_point = Point(
    #     round(interpolated_source_point.x, 5),
    #     round(interpolated_source_point.y, 5),
    #     srid=4326,
    # )
    # interpolated_destination_point = Point(
    #     round(interpolated_destination_point.x, 5),
    #     round(interpolated_destination_point.y, 5),
    #     srid=4326,
    # )
    segment_poly = segment_polyline(ls, interpolated_destination_point)

    print("segment_poly ", GEOSGeometry(segment_poly[0])[0][0], "\n")



    interpolated_source_point = Point(
        rounding(interpolated_source_point.x),
        rounding(interpolated_source_point.y),
        srid=4326,
    )
    interpolated_destination_point = Point(
        rounding(interpolated_destination_point.x),
        rounding(interpolated_destination_point.y),
        srid=4326,
    )

    if interpolated_source_point not in ls:
        ls.append(tuple(interpolated_source_point))
    if interpolated_destination_point not in ls:
        ls.append(tuple(interpolated_destination_point))
    print("here")

    reference_point_start = Point(ls[0])

    # ls_with_distance_list = [x[1] for x in
    #                          [(Point(point).distance(reference_point_start), point) for point in ls]
    #
    #                          ]
    ls_with_distance_list = [point for point in ls]

    index_interpolated_source_point = ls_with_distance_list.index(tuple(interpolated_source_point))
    index_interpolated_destination_point = ls_with_distance_list.index(tuple(interpolated_destination_point))

    polyline_points_list = ls_with_distance_list
    # if index_interpolated_destination_point > index_interpolated_source_point:
    #     polyline_points_list = ls_with_distance_list[
    #                            index_interpolated_source_point:index_interpolated_destination_point + 1
    #                            ]
    # else:
    #     polyline_points_list = ls_with_distance_list[
    #                            index_interpolated_destination_point:index_interpolated_source_point + 1
    #                            ]

    print(
        "Interpolated",
        reference_point_start, "\n",
        # polyline_points_list, "\n",
        interpolated_source_point, "\n",
        interpolated_destination_point, "\n",
        ls_with_distance_list, "\n",
        index_interpolated_source_point, index_interpolated_destination_point
    )
    # llok for dups
    duplist = []
    for point in polyline_points_list:
        if point in duplist:
            continue
        else:
            duplist.append(point)

    print("duplist ", duplist)
    polyline_points_dict = [
        {
            "latitude": point[0],
            "longitude": point[1]
        } for point in duplist
    ]
    distance = round(
        (interpolated_destination_point.distance(interpolated_source_point) *
         2 * math.pi * 6378.137
         / 360
         * 1000), 3
    )
    duration = distance * 1.5

    if duration > 3600:
        duration /= 3600
        duration = f"{int(duration)} hr"
    elif duration > 60:
        duration /= 60
        duration = f"{int(duration)} min"
    else:
        duration = f"{round(duration, 2)} sec"

    response_json = {
        "distance": f"{distance} m",
        "duration": f"{duration}",
        "polyline": polyline_points_dict
    }
    print("duration", duration, distance)

    return response_json

"""

def get_directions(transaction_id, source_dict, destination_dict):
    # transaction_id = 787
    # into coordinate strings for api call
    source = f"{source_dict['latitude']}, {source_dict['longitude']}"
    destination = f"{destination_dict['latitude']}, {destination_dict['longitude']}"

    # initial deviation
    source_deviation = destination_deviation = 0

    # source and destination points
    source_point = Point(source_dict['latitude'], source_dict['longitude'], srid=4326)
    destination_point = Point(destination_dict['latitude'], destination_dict['longitude'], srid=4326)

    poly = PolyLine.objects.filter(transaction=transaction_id)
    if poly.exists():
        poly_obj = poly.first()
    else:
        poly_obj = PolyLine.objects.create(
            transaction=transaction_id,
            seeker_location=Point(source_dict['longitude'], source_dict['latitude'], srid=4326),
            provider_location=Point(destination_dict['longitude'], destination_dict['latitude'], srid=4326)
        )

    # polyline was previously created
    if poly_obj.linestring is not None:
        # source deviation
        source_deviation = poly_obj.linestring.distance(source_point)
        destination_deviation = poly_obj.linestring.distance(destination_point)
    print(destination_deviation, degress_to_meters(destination_deviation))
    print("deviations:",source_deviation, degress_to_meters(source_deviation))
    # if polyline line string newly created or there is significant deviation
    if (
            poly_obj.linestring is None or
            degress_to_meters(source_deviation) > 50 or
            degress_to_meters(destination_deviation) > 50
    ):
        direction_response = call_maps_api(source, destination)
        polyline_points = polyline_to_latlong(direction_response["polyline"])
        poly_obj.linestring = LineString(polyline_points)
        poly_obj.save()

        polyline_points_list = []
        for point in polyline_points:
            polyline_points_list.append({
                "latitude": point[0],
                "longitude": point[1]
            })

        return {
            "distance": direction_response["distance"],
            "duration": direction_response["duration"],
            "polyline": polyline_points_list
        }

    # polyline cut
    ls = poly_obj.linestring
    print("linestring print", ls)


    # source cut
    interpolated_source_point = ls.interpolate(ls.project(source_point))
    interpolated_destination_point = ls.interpolate(ls.project(destination_point))

    segment_poly_source = segment_polyline(ls, interpolated_source_point)
    new_ls = GEOSGeometry(segment_poly_source[0])[-1]
    new_ls.srid = 4326
    final_segment_poly= segment_polyline(new_ls, interpolated_destination_point)
    # final_segment_poly= segment_poly_source

    print("segment_poly ", type(GEOSGeometry(final_segment_poly[0])[0]), type(ls),
          GEOSGeometry(final_segment_poly[0])[0],
          # GEOSGeometry(final_segment_poly[0])[1],
          "\n")


    print(
        "Interpolated",
        # polyline_points_list, "\n",
        interpolated_source_point, "\n",
        interpolated_destination_point, "\n",
        # index_interpolated_source_point, index_interpolated_destination_point
    )
    # llok for dups
    duplist = []
    # if interpolated_destination_point in GEOSGeometry(final_segment_poly[0])[0] and interpolated_source_point in GEOSGeometry(final_segment_poly[0])[0]:
    #     final_geom = GEOSGeometry(final_segment_poly[0])[0]
    # else:
    #     final_geom = GEOSGeometry(final_segment_poly[0])[1]

    for point in GEOSGeometry(final_segment_poly[0])[0]:
        if point in duplist:
            continue
        else:
            duplist.append(point)
    # duplist.append(destination_point)

    distance = round(
        (interpolated_destination_point.distance(interpolated_source_point) *
         2 * math.pi * 6378.137
         / 360
         * 1000), 3
    )

    if GEOSGeometry(final_segment_poly[0])[0] ==GEOSGeometry(final_segment_poly[0])[-1] and distance < 40:
        duplist = LineString(interpolated_destination_point, interpolated_source_point, srid=4326)

    print("duplist ", duplist)
    polyline_points_dict = [
        {
            "latitude": point[0],
            "longitude": point[1]
        } for point in duplist
    ]

    duration = distance * 1.5

    if duration > 3600:
        duration /= 3600
        duration = f"{int(duration)} hr"
    elif duration > 60:
        duration /= 60
        duration = f"{int(duration)} min"
    else:
        duration = f"{round(duration, 2)} sec"

    response_json = {
        "distance": f"{distance} m",
        "duration": f"{duration}",
        "polyline": polyline_points_dict
    }
    print("duration", duration, distance)

    return response_json

# reverse geocoding
def latlong_to_address(latlong):
    # url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlong}&key={settings.GOOGLE_MAPS_API_KEY}"
    # re_geo_response = requests.request("GET", url)
    # try:
    #     formatted_address = re_geo_response.json()["results"][0]["formatted_address"]
    #     place_id = re_geo_response.json()["results"][0]["place_id"]
    # except:
    #     formatted_address = re_geo_response.json()["results"][0]["formatted_address"]
    #     place_id = re_geo_response.json()["results"][0]["place_id"]
    # return {
    #     "formatted_address": formatted_address,
    #     "place_id": place_id
    # }
    # dev data
    return {
        "formatted_address": '7 Gareeb-e-Nawaz Ave, Dhaka 1230, Bangladesh',
        'place_id': 'ChIJVRuudV3FVTcRtpi3AmwBTSI'
    }
