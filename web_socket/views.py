from rest_framework import (
    permissions,
    response,
    status,
    views,
    serializers,
)
from utils.apps.web_socket import send_message_to_channel, coin_change
from django.core.cache import cache
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, extend_schema_serializer


class CancelSearchSerializer(serializers.Serializer):
    cancel = serializers.BooleanField(default=False)


class PreferredNoteSearchResponse(serializers.Serializer):
    note_list = serializers.ListField(child=serializers.CharField())
    total = serializers.FloatField(default=0.0)
    commission = serializers.FloatField(default=0.0)


class PreferredNoteSearch(serializers.Serializer):
    initial_note = serializers.CharField()
    five_hundred = serializers.IntegerField(allow_null=True)
    two_hundred = serializers.IntegerField(allow_null=True)
    one_hundred = serializers.IntegerField(allow_null=True)
    fifty = serializers.IntegerField(allow_null=True)
    twenty = serializers.IntegerField(allow_null=True)
    ten = serializers.IntegerField(allow_null=True)


class CancelSearch(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, *args, **kwargs):
        # if "cancel" in self.request.data:
        #     if self.request.data.get("cancel"):
        try:
            cache.delete(str(self.request.user.id))
            return response.Response(
                {"detail": "cancel request sent to socket"},
                status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(
                {"errors": f"{e};cancel request could not be sent"},
                status=status.HTTP_400_BAD_REQUEST)


class PreferredSearch(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PreferredNoteSearch

    @extend_schema(
        request=PreferredNoteSearch,
        responses=PreferredNoteSearchResponse,
    )
    def post(self, *args, **kwargs):
        print(self.request.data, self.request.user)
        initial_note = self.request.data.get("initial_note")
        try:
            initial_note = int(initial_note)
        except:
            return response.Response({"detail": "Enter Valid data"}, status=status.HTTP_400_BAD_REQUEST)


        five_hundred = self.request.data.get("five_hundred", 0)
        two_hundred = self.request.data.get("two_hundred", 0)
        one_hundred = self.request.data.get("one_hundred", 0)
        fifty = self.request.data.get("fifty", 0)
        twenty = self.request.data.get("twenty", 0)
        ten = self.request.data.get("ten", 0)

        #
        if (
                (five_hundred * 500) +
                (two_hundred * 200) +
                (one_hundred * 100) +
                (fifty * 50) +
                (twenty * 20) +
                (ten * 10) > initial_note
        ):
            return response.Response(
                {"detail": "Amount Exceeded"},
                status=status.HTTP_400_BAD_REQUEST)



        note_list = coin_change(
            initial_note,
            five_hundred=five_hundred,
            two_hundred=two_hundred,
            one_hundred=one_hundred,
            fifty=fifty,
            twenty=twenty,
            ten=ten,
        )
        if note_list == -1:
            return response.Response(
                {"detail": "Note combination do not exist"},
                status=status.HTTP_400_BAD_REQUEST)

        # note_message = f"note list is {x}"
        # note_list =
        # print("x".join([f"{x}" for x in note_list]))
        return response.Response(
            # {"detail": f'Note combination is {"x".join([f"{x}" for x in note_list])}'},
            {
                # "notes": "x".join([f"{x}" for x in note_list]),
                "note_list": [f"{x}" for x in note_list],
                "total": initial_note - settings.PROVIDER_COMMISSION,
                "commission": settings.PROVIDER_COMMISSION
            },
            status=status.HTTP_200_OK)
