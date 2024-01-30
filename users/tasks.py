from core.celery import app
from .models import *
from datetime import datetime

@app.task
def user_deletion_routine_task():
    users_to_be_deleted = UsersDeletionSchedule.objects.all()
    users_to_be_deleted_final = list(users_to_be_deleted.filter(
        user__is_active=False,
        time_of_deletion=datetime.now().date()
    ).values_list('user__id', flat=True))
    print("users to be deleted", users_to_be_deleted_final)
    user_deleted = User.objects.filter(id__in=users_to_be_deleted_final).delete()
    users_to_be_deleted.delete()
    print("users has been deleted", user_deleted)
