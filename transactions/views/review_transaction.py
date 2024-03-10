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
from utils.apps.transaction import get_transaction_id
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from utils.custom_pagination import CustomPagination


# class TransactionRatingViewSet(viewsets.ModelViewSet):
#     queryset = TransactionAsSeekerReview.objects.all()
#     serializer_class = TransactionAsSeekerReviewSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'transaction_no'
#     http_method_names = ["post", ]
#
#     def create(self, request, *args, **kwargs):
#         user = self.request.user
#         serializer = self.serializer_class(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             review = serializer.save()
#             if review == -1:
#                 return response.Response({"error": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
#             if review == -2:
#                 return response.Response({"error": "User not authorised to rate this transaction"},
#                                          status=status.HTTP_403_FORBIDDEN)
#             return response.Response(serializer.data, status=status.HTTP_201_CREATED)
#         return response.Response("", status=status.HTTP_400_BAD_REQUEST)
#

class TransactionMessagesViewSet(viewsets.ModelViewSet):
    queryset = TransactionMessages.objects.all()
    serializer_class = TransactionMessagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["get", ]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.none()
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False,pagination_class=CustomPagination)
    def retrieve(self, request, *args, **kwargs):
        transaction_no = kwargs.get("transaction_no")
        transaction_id = get_transaction_id(transaction_no)
        transaction_obj = Transaction.objects.get(id=transaction_id)
        if request.user not in [transaction_obj.seeker, transaction_obj.provider]:
            return response.Response(
                {"errors": "User not allowed to view this transaction messages"}, status=status.HTTP_403_FORBIDDEN
            )
        queryset = self.queryset.filter(transaction=transaction_id).order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class TransactionAsSeekerReviewViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsSeekerReview.objects.all()
    serializer_class = TransactionAsSeekerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response({"error": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response({"error": "User not authorised to rate this transaction"},
                                         status=status.HTTP_403_FORBIDDEN)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)


class TransactionAsProviderReviewViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsProviderReview.objects.all()
    serializer_class = TransactionAsProviderReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response({"error": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response({"error": "User not authorised to rate this transaction"},
                                         status=status.HTTP_403_FORBIDDEN)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)


class TransactionAsProviderAbuseReportViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsProviderAbuseReport.objects.all()
    serializer_class = TransactionAsProviderAbuseReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response({"error": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response({"error": "User not authorised to rate this transaction"},
                                         status=status.HTTP_403_FORBIDDEN)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)


class TransactionAsSeekerAbuseReportViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsSeekerAbuseReport.objects.all()
    serializer_class = TransactionAsSeekerAbuseReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response({"error": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response({"error": "User not authorised to rate this transaction"},
                                         status=status.HTTP_403_FORBIDDEN)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("", status=status.HTTP_400_BAD_REQUEST)
