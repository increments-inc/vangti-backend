from rest_framework import exceptions, serializers, validators
from ..models import *


class VangtiSearchSerializer(serializers.Serializer):
    note = serializers.IntegerField(max_value=1000, min_value=100)
    preferred_notes = serializers.ListField(child=serializers.CharField())