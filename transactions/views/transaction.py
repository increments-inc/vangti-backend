from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
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


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


# history and insights
class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def provider_history(self, *args, **kwargs):
        user = self.request.user
        queryset = self.queryset.filter(provider=user)
        if queryset:
            serializer = self.serializer_class(queryset)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return response.Response(
            "No Data found",
            status=status.HTTP_404_NOT_FOUND
        )

    def seeker_history(self, *args, **kwargs):
        user = self.request.user
        queryset = self.queryset.filter(seeker=user)
        if queryset:
            serializer = self.serializer_class(queryset)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return response.Response(
            "No Data found",
            status=status.HTTP_404_NOT_FOUND
        )
