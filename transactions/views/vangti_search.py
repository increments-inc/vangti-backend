from django.core.mail import send_mail
from django.conf import settings
from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from ..serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache


class VangtiSearch(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VangtiSearchSerializer

    @method_decorator(login_required)  # Ensure user is logged in
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # create room, send room id
            return Response(serializer.data, status=status.HTTP_200_OK)

