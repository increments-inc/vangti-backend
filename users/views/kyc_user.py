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


class UserNidInformationViewSet(viewsets.ModelViewSet):
    queryset = UserNidInformation.objects.all()
    serializer_class = AddNidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def add_nid(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    # send to porichoy/something
    def validate_information(self, *args, **kwargs):
        return response.Response("", status=status.HTTP_200_OK)


class UserKYCInformationViewSet(viewsets.ModelViewSet):
    queryset = UserKYCInformation.objects.all()
    serializer_class = AddKycSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'update_kyc_information':
            return UpdateKycSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def add_kyc_info(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def update_kyc_information(self, request, *args, **kwargs):
        instance = self.request.user.user_kyc
        print(instance)
        serializer = self.get_serializer_class()(instance, data=self.request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)