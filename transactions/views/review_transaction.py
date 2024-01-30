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

    def get_serializer_class(self):
        if self.action == "rate_transaction":
            return TransactionReviewRetrieveSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        user = self.request.user
        data = self.request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("", status=status.HTTP_204_NO_CONTENT)

    def rate_transaction(self, request, *args, **kwargs):
        transaction = request.data.get("transaction", None)
        queryset = self.queryset.filter(transaction=transaction)
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

