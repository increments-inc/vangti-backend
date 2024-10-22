from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from django.db.models import Q
from ..serializers import *
from ..tasks import *
from utils.apps.location import get_user_list as get_user_set
from utils.apps.analytics import get_home_analytics_of_user_set
from django.core.cache import cache


class UserServiceModeViewSet(viewsets.ModelViewSet):
    queryset = UserServiceMode.objects.all()
    serializer_class = UserServiceModeSerializer
    permission_classes = [permissions.IsAuthenticated]

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
        # kyc dependency
        # try:
        #     self.request.user.users_verified
        # except ObjectDoesNotExist:
        #     return response.Response(
        #         {"message": "User not verified"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        if Transaction.objects.filter(
                Q(seeker=self.request.user) | Q(provider=self.request.user)
        ).filter(
            is_completed=False
        ).exists():
            logger.info("open deals exists")
            return response.Response(
                {
                    "errors": "Cannot change mode while transaction is ongoing"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if cache.get(f"{str(self.request.user.id)}-timestamp") is not None:
            return response.Response(
                {
                    "errors": "Cannot change mode while search is ongoing"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            self.perform_update(serializer)

            # send out updated analytics to users
            user_set = get_user_set(self.request.user)
            final_user_list = []

            if user_set:
                for user in user_set:
                    surrounding_user_set = get_user_set(user)
                    surrounding_analytics = get_home_analytics_of_user_set(surrounding_user_set)
                    if surrounding_analytics is not None:
                        #     surrounding_analytics = []
                        # else:
                        surrounding_analytics["user"] = str(user.id)
                        final_user_list.append(surrounding_analytics)
                        print(surrounding_analytics)
                send_out_analytics_mesg.delay(final_user_list)

            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return response.Response("", status=status.HTTP_400_BAD_REQUEST)
