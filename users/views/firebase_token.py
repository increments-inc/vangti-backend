from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from ..serializers import *
from ..app_utils import get_reg_token
from django.conf import settings


class UserFirebaseTokenViewSet(viewsets.ModelViewSet):
    queryset = UserFirebaseToken.objects.all()
    serializer_class = UserFirebaseTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    def create(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data, context={"request": self.request})
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response({"errors": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


