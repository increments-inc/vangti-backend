from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from ..serializers import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class UserServiceModeViewSet(viewsets.ModelViewSet):
    queryset = UserServiceMode.objects.all()
    serializer_class = UserServiceModeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_serializer_class(self):
    #     if self.action == 'mode_change':
    #         return UserServiceModeChangeSerializer
    #     return self.serializer_class

    def get_mode(self, *args, **kwargs):
        serializer = self.serializer_class(self.queryset.get(user=self.request.user), context={'request': self.request})
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def mode_change(self, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        data = self.request.data
        serializer = self.serializer_class(instance, data=data, context={"request": self.request})
        try:
            self.request.user.users_verified
        except ObjectDoesNotExist:
            return response.Response(
                {"message": "User not verified"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Transaction.objects.filter(
                Q(seeker=self.request.user) | Q(provider=self.request.user)
        ).filter(
            is_completed=False
        ).exists():
            print("open deals exists")
            return response.Response(
                {
                    "errors": "Cannot change mode while transaction is ongoing"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            self.perform_update(serializer)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return response.Response("", status=status.HTTP_400_BAD_REQUEST)
