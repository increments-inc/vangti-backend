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
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class TransactionRequests(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(login_required)  # Ensure user is logged in
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        return Response("will accept the transaction request", status=status.HTTP_200_OK)


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
