from django.contrib.gis.db import models
import uuid
from core.abstract_models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(BaseModel):
    name = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        verbose_name="ID"
    )
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_provider")
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_seeker")


class ChatHistory(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_chat_history")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_history_user")
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("room", "-created_at",)


class CallHistory(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_call_history")
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="call_history_caller")
    callee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="call_history_callee")
    duration = models.DurationField()

    class Meta:
        ordering = ("room", "-created_at",)

