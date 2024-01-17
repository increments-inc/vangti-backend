from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from .serializers import *
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView


class LocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "post"]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)

    def get_location(self, *args, **kwargs):
        serializer = self.serializer_class(
            self.get_queryset().get(user=self.request.user.id)
        )
        return response.Response(serializer.data,status=status.HTTP_200_OK)

    def post_location(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data, context={"request": self.request})
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)


    def update_location(self, *args, **kwargs):
        instance = self.get_queryset().get(user=self.request.user.id)
        serializer = self.serializer_class(instance, data=self.request.data, context={"request": self.request})
        if serializer.is_valid():
            super().perform_update(serializer)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
