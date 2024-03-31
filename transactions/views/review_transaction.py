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
from utils.apps.analytics_rating import (
    at_seeker_rating_update, at_provider_rating_update,
    at_seeker_abuse_rep_update, at_provider_abuse_rep_update
)
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from utils.custom_pagination import CustomPagination


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

    @extend_schema(
        request=TransactionAsSeekerReviewSerializer,
        responses=TransactionSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response(
                    {"errors": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response(
                    {"errors": "User not authorised to rate this transaction"},
                    status=status.HTTP_403_FORBIDDEN)

            # update rating
            at_seeker_rating_update(request.user)

            transaction_serializer = TransactionSerializer(review.transaction, context={"request": request})

            return response.Response(transaction_serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(
            {"errors": [i[0] for i in serializer.errors.values()]},
            status=status.HTTP_400_BAD_REQUEST)


class TransactionAsProviderReviewViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsProviderReview.objects.all()
    serializer_class = TransactionAsProviderReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    @extend_schema(
        request=TransactionAsProviderReviewSerializer,
        responses=TransactionSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response(
                    {"errors": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response(
                    {"errors": "User not authorised to rate this transaction"},
                    status=status.HTTP_403_FORBIDDEN)

            # update rating
            at_provider_rating_update(request.user)

            transaction_serializer = TransactionSerializer(review.transaction, context={"request": request})

            return response.Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
        # print("se",[i for i in [i[0] for i in serializer.errors.values()]}.values()], [i[0] for i in serializer.errors.values()]})
        return response.Response({"errors": [i[0] for i in serializer.errors.values()]},
                                 status=status.HTTP_400_BAD_REQUEST)


class TransactionAsProviderAbuseReportViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsProviderAbuseReport.objects.all()
    serializer_class = TransactionAsProviderAbuseReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    @extend_schema(
        request=TransactionAsProviderAbuseReportSerializer,
        responses=TransactionSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response(
                    {"errors": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response(
                    {"errors": "User not authorised to rate this transaction"},
                    status=status.HTTP_403_FORBIDDEN)

            # update abuse rep count
            at_provider_abuse_rep_update(self.request.user)

            transaction_serializer = TransactionSerializer(review.transaction, context={"request": request})

            return response.Response(transaction_serializer.data, status=status.HTTP_201_CREATED)

            # return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response({"errors": [i[0] for i in serializer.errors.values()]},
                                 status=status.HTTP_400_BAD_REQUEST)


class TransactionAsSeekerAbuseReportViewSet(viewsets.ModelViewSet):
    queryset = TransactionAsSeekerAbuseReport.objects.all()
    serializer_class = TransactionAsSeekerAbuseReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["post", ]

    @extend_schema(
        request=TransactionAsSeekerAbuseReportSerializer,
        responses=TransactionSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            review = serializer.save()
            if review == -1:
                return response.Response(
                    {"errors": "No valid transaction found"}, status=status.HTTP_400_BAD_REQUEST)
            if review == -2:
                return response.Response(
                    {"errors": "User not authorised to rate this transaction"},
                    status=status.HTTP_403_FORBIDDEN)

            # update abuse rep count
            at_seeker_abuse_rep_update(self.request.user)
            transaction_serializer = TransactionSerializer(review.transaction, context={"request": request})

            return response.Response(transaction_serializer.data, status=status.HTTP_201_CREATED)

            # return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response({"errors": [i[0] for i in serializer.errors.values()]},
                                 status=status.HTTP_400_BAD_REQUEST)
