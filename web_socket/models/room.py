import uuid
from core.abstract_models import models, BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


# class Room(BaseModel):
#     name = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         verbose_name="ID"
#     )
#     provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_provider", null=True, blank=True)
#     seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_seeker", null=True, blank=True)


class SocketRoom(BaseModel):
    name = models.CharField(max_length=50, null=True)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_provider", null=True, blank=True)
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_seeker", null=True, blank=True)


class RoomMessages(BaseModel):
    room = models.ForeignKey(SocketRoom, on_delete=models.CASCADE, related_name="room_chat_history")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_history_user")
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("room", "-created_at",)


# class CallHistory(BaseModel):
#     room = models.ForeignKey(SocketRoom, on_delete=models.CASCADE, related_name="room_call_history")
#     caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="call_history_caller")
#     callee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="call_history_callee")
#     duration = models.DurationField()
#
#     class Meta:
#         ordering = ("room", "-created_at",)

