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
from .models import *
from .serilaizers import *


def send_email(user):
    host_user = settings.EMAIL_HOST_USER

    send_mail(
        "Vangti OTP",
        f"dummy mail {user}",
        host_user,
        [host_user],
        fail_silently=False,
    )
    input_letter = input("enter a number")
    return


def transaction_request_method(user_list):
    for user in user_list:
        send_email(user)

    return


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


class TransactionReviewViewSet(viewsets.ModelViewSet):
    queryset = TransactionReview.objects.all()
    serializer_class = TransactionReviewSerializer
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


class UserServiceModeViewSet(viewsets.ModelViewSet):
    queryset = UserServiceMode.objects.all()
    serializer_class = UserServiceModeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # http_method_names = ["patch"]

    def mode_change(self, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        data = self.request.data
        serializer = self.serializer_class(instance, data=data)
        if serializer.is_valid():
            # serializer.save()
            self.perform_update(serializer)

            return response.Response(
                "patch success",
                status=status.HTTP_200_OK
            )
        return response.Response("", status=status.HTTP_200_OK)
