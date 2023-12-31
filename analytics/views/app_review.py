from rest_framework import viewsets, status
from ..serializers import *


class AppFeedbackViewSet(viewsets.ModelViewSet):
    queryset = AppFeedback.objects.all()
    serializer_class = AppFeedbackSerializer
    http_method_names = ["post",]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

