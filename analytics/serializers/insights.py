from rest_framework import exceptions, serializers, validators
from ..models import *


class InsightsListSerializer(serializers.Serializer):
    date = serializers.CharField(default="2001-01-01 00:00:00")
    total_amount_of_transaction = serializers.FloatField(default=0.0)
    profit = serializers.FloatField(default=0.0)
    no_of_transaction = serializers.IntegerField(default=0)


class AvgTransactionSerializer(serializers.Serializer):
    no_of_transaction = serializers.IntegerField(default=0)
    total_amount_of_transaction = serializers.FloatField(default=0.0)
    amount_stat = serializers.FloatField(default=0.0)
    num_stat = serializers.FloatField(default=0.0)


class DemandedVangtiSerializer(serializers.Serializer):
    interval = serializers.CharField(default="daily")
    note = serializers.CharField(default="0")
    stat = serializers.FloatField(default=0.0)
