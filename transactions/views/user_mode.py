from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from ..serializers import *


class UserServiceModeViewSet(viewsets.ModelViewSet):
    queryset = UserServiceMode.objects.all()
    serializer_class = UserServiceModeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # http_method_names = ["patch"]

    def mode_change(self, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        data = self.request.data
        serializer = self.serializer_class(instance, data=data)
        if serializer.is_valid():
            # serializer.save()
            self.perform_update(serializer)

            return response.Response(
                "patch success",
                status=status.HTTP_200_OK
            )
        return response.Response("", status=status.HTTP_200_OK)
