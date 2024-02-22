from rest_framework import (
    permissions,
    response,
    status,
    views,
    serializers,
)
from utils.apps.web_socket import send_message_to_channel
from django.core.cache import cache


class CancelSearchSerializer(serializers.Serializer):
    cancel = serializers.BooleanField(default=False)


class CancelSearch(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    # serializer_class = CancelSearchSerializer

    def post(self, *args, **kwargs):
        print("here in post", self.request.data, self.request.user)
        # if "cancel" in self.request.data:
        #     if self.request.data.get("cancel"):
        print("cache", cache.get(str(self.request.user.id)))
        try:
            cache.delete(str(self.request.user.id))
            return response.Response(
                {"detail": "cancel request sent to socket"},
                status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(
                {"errors": f"{e};cancel request could not be sent"},
                status=status.HTTP_400_BAD_REQUEST)
