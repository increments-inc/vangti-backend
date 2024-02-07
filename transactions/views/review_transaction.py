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


class TransactionRatingViewSet(viewsets.ModelViewSet):
    queryset = TransactionReview.objects.all()
    serializer_class = TransactionReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["get", "post", ]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response({"error": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response({"error": "User not authorised to rate this transaction"}, status=status.HTTP_403_FORBIDDEN)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)
