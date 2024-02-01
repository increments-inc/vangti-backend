from rest_framework import exceptions, serializers, validators
from .. import models
from datetime import datetime, timedelta


class UsersDeletionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UsersDeletionSchedule
        fields = ("id",)
        read_only_fields = ["time_of_deletion", "user__phone_number"]

    def create(self, validated_data):
        user = self.context.get('request').user
        user.is_active = False

        schedule = models.UsersDeletionSchedule.objects.create(
            user=user,
            time_of_deletion=datetime.now().date() + timedelta(days=30)
        )
        user.save()
        return schedule
