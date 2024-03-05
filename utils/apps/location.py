import polyline
from django.conf import settings
import requests
from django.contrib.gis.measure import D
from locations.models import PolyLine, UserLocation
from django.contrib.gis.geos import Point, LineString
from django.contrib.gis.db.models.functions import Distance
from users.models import User


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


def call_maps_api(source, destination):
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source}&destination={destination}&key={settings.GOOGLE_MAPS_API_KEY}&mode=walking"
    direction_response = requests.request("GET", directions_url)
    response = direction_response.json()
    print("DIRECTION API CALLED !!! \n", )

    return {
        "distance": response["routes"][0]["legs"][0]["distance"]["text"],
        "duration": response["routes"][0]["legs"][0]["duration"]["text"],
        "polyline": response['routes'][0]['overview_polyline']["points"]
    }


def get_directions(transaction_id, source_dict, destination_dict):
    # transaction_id=787
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
            seeker_location = Point(source_dict['longitude'], source_dict['latitude'], srid=4326),
            provider_location=Point(destination_dict['longitude'], destination_dict['latitude'], srid=4326)
        )

    # polyline was previously created
    if poly_obj.linestring is not None:
        # source deviation
        source_deviation = PolyLine.objects.filter(
            transaction=transaction_id
        ).annotate(
            distance=Distance("linestring", source_point)
            # ).values(
            #     "linestring", "distance"
        ).values("distance").first()["distance"].km

        destination_deviation = PolyLine.objects.filter(
            transaction=transaction_id
        ).annotate(
            distance=Distance("linestring", destination_point)
            # ).values(
            #     "linestring", "distance"
        ).values("distance").first()["distance"].km

    # if polyline line string newly created or there is significant deviation
    if (
            poly_obj.linestring is None or
            source_deviation > 3000000 or
            destination_deviation > 3000000
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
    source_point_in_ls = ls.interpolate(ls.project(source_point))
    new_source_point = Point(source_point_in_ls.y, source_point_in_ls.x, srid=4326)
    new_scoords = ls.coords.index(tuple(source_point_in_ls))
    print("new  source  ", new_scoords, new_source_point)

    # destination cut
    destination_point_in_ls = ls.interpolate(ls.project(destination_point))
    new_destination_point = Point(destination_point_in_ls.y, destination_point_in_ls.x, srid=4326)
    new_dcoords = ls.coords.index(tuple(destination_point_in_ls))
    print("new  destination  ", new_dcoords, new_destination_point)

    list_ls = []
    # inserting new source and destination
    if new_dcoords > new_scoords:
        list_ls = ls[new_scoords: new_dcoords + 1]
        list_ls.insert(0, new_source_point)
        list_ls.append(new_destination_point)
    if new_dcoords < new_scoords:
        list_ls = ls[new_dcoords: new_scoords + 1]
        list_ls.insert(0, new_destination_point)
        list_ls.append(new_source_point)
    if new_dcoords == new_scoords:
        list_ls = ls

    empty_point_list = []
    for point in list_ls:
        empty_point_list.append({
            "latitude": point[0],
            "longitude": point[1]
        })
    source_p = Point(empty_point_list[0]["longitude"], empty_point_list[0]["latitude"])
    des_p = Point(empty_point_list[-1]["longitude"], empty_point_list[-1]["latitude"])

    print("list ls", list_ls[0])
    # distance = D(m=
    #     source_p.transform(4326, clone=True).distance(
    #         des_p.transform(4326, clone=True)
    #     )
    # )
    duration = 0 * 1.5 * 1000

    if duration > 3600:
        duration /= 3600
        duration = f"{int(duration)} hr"
    elif duration > 60:
        duration /= 60
        duration = f"{int(duration)} min"
    else:
        duration = f"{duration} sec"
    response_json = {
        "distance": f"{0}",
        "duration": f"{duration}",
        "polyline": empty_point_list
    }
    print("duration", duration, response_json)

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
