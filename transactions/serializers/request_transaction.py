from rest_framework import exceptions, serializers, validators
from ..models import *
from django.core.cache import cache
from locations.models import UserLocation

class VangtiSearchSerializer(serializers.Serializer):
    note = serializers.IntegerField(max_value=1000, min_value=100)
    preferred_notes = serializers.ListField(child=serializers.CharField())
    


class TransactionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionRequest
        # fields = "__all__"
        exclude = ["seeker",]
        read_only_fields = ["id", "provider", "is_affirmed", "seeker"]

    def create(self, validated_data):
        user = self.context.get("request").user
        try:
            t_req = TransactionRequest.objects.get(
                seeker=user
            )
            t_req.amount = validated_data.get("amount")
            t_req.preferred_notes = validated_data.get("preferred_notes")
            t_req.save()
        except TransactionRequest.DoesNotExist:
            t_req = TransactionRequest.objects.create(
                **validated_data
            )
        # cache
        # user_loc_list = UserLocation.objects.get(
        #     user = user.id
        # ).location_radius_userlocation.user_id_list
        # cache.set(f"{user.id}", user_loc_list, timeout=None)

        return t_req
