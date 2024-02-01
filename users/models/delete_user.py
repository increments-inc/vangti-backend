from core.abstract_models import models, BaseModel
from .basic_user import User


class UsersDeletionSchedule(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_delettion_schedule_user"
    )
    is_to_be_deleted = models.BooleanField(default=True)
    time_of_deletion = models.DateField()

    class Meta:
        ordering = ("user",)
