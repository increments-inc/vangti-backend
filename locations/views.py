from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from .serializers import LocationSerializer, GoogleMapsSerializer, UserLocation


# from .models import UserLocation


class LocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.using('location').all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "post"]

    def get_serializer_class(self):
        if self.action == "get_reverse_geocode":
            return GoogleMapsSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)

    # def get_location(self, *args, **kwargs):
    #     serializer = self.serializer_class(
    #         self.get_queryset().get(user=self.request.user.id)
    #         # self.get_object()
    #     )
    #     return response.Response(serializer.data, status=status.HTTP_200_OK)

    # def post_location(self, *args, **kwargs):
    #     serializer = self.serializer_class(data=self.request.data, context={"request": self.request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return response.Response(
    #             serializer.data,
    #             status=status.HTTP_200_OK
    #         )
    #     return response.Response("", status=status.HTTP_400_BAD_REQUEST)

    def update_location(self, *args, **kwargs):
        # print("helo", self.request.META.get('HTTP_AUTHORIZATION') )
        try:
            instance = self.get_queryset().get(user=self.request.user.id)
            serializer = self.serializer_class(instance, data=self.request.data, context={"request": self.request})
            if serializer.is_valid():
                super().perform_update(serializer)
        except UserLocation.DoesNotExist:
            instance = UserLocation.objects.create(
                user=self.request.user.id,
                user_phone_number=self.request.user.phone_number,
                latitude=self.request.data["latitude"],
                longitude=self.request.data["longitude"],
                # **self.request.data
            )
            serializer = self.serializer_class(instance, context={"request": self.request})

        # serializer = self.serializer_class(instance, data=self.request.data, context={"request": self.request})
        # if serializer.is_valid():
        #     super().perform_update(serializer)
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def get_reverse_geocode(self, *args, **kwargs):
        try:
            instance = self.get_queryset().get(user=self.request.user.id)
            serializer = self.get_serializer_class()(instance, context={"request": self.request})

            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except:
            return response.Response(
                {
                    "latitude": 0,
                    "longitude": 0,
                    "google_api_data": {
                        "formatted_address": "No address found",
                        "place_id": "No place id found"
                    }},
                status=status.HTTP_200_OK
            )
