from rest_framework import (
    permissions,
    response,
    status,
    views,
    serializers,
)
from utils.apps.web_socket import send_message_to_channel


class CancelSearchSerializer(serializers.Serializer):
    cancel = serializers.BooleanField(default=False)


class CancelSearch(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CancelSearchSerializer

    def post(self, *args, **kwargs):
        print("here in post", self.request.data, self.request.user)
        if "cancel" in self.request.data:
            # cancel_search = self.request.data.pop("cancel")
            # if cancel_search:
            #     message = {}

            message = {
                "request": "CANCEL_TRANSACTION",
                "status": "CANCELLED",
                "data" : {
                    "transaction_id": None
                }
            }
            send_message_to_channel(self.request, self.request.user, message)
        # usernames = [user.username for user in User.objects.all()]
        return response.Response({"detail": "cancel request sent to socket"}, status=status.HTTP_200_OK)
