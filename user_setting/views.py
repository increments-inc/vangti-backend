from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from .serializers import *


class UserSettingViewSet(viewsets.ModelViewSet):
    queryset = UserSetting.objects.all()
    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'edit_language':
            return UserLanguageSerializer
        if self.action == 'edit_terms':
            return UserTermsSerializer
        return self.serializer_class

    def edit_language(self, request, *args, **kwargs):
        instance = self.queryset.filter(user=self.request.user).first()
        serializer = self.get_serializer_class()(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)

    def edit_terms(self, request, *args, **kwargs):
        instance = self.queryset.filter(user=self.request.user).first()
        serializer = self.get_serializer_class()(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)

    def get_setting(self, request, *args, **kwargs):
        instance = self.queryset.filter(user=self.request.user).first()
        serializer = self.get_serializer_class()(instance)
        return response.Response(
            serializer.data, status=status.HTTP_200_OK
        )


class VangtiTermsViewSet(viewsets.ModelViewSet):
    queryset = VangtiTerms.objects.all()
    serializer_class = VangtiTermsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def get_terms(self, *ars, **kwargs):
        instance = self.queryset.last()
        serializer = self.get_serializer_class()(instance,
                                                 # context={"request": self.request}
                                                 )
        return response.Response(
            serializer.data, status=status.HTTP_200_OK
        )
