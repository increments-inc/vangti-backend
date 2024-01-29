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
    lookup_field = 'transaction_no'
    http_method_names = ["get", "patch"]

    def list(self, request, *args, **kwargs):
        # no list shown
        queryset = self.queryset.none()
        serializer = self.serializer_class(queryset, many=True, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # print(kwargs)
        transaction_id = kwargs[self.lookup_field][8:]
        instance = self.queryset.get(id=int(transaction_id))
        serializer = self.serializer_class(instance, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)


"""
def transaction_id(start_id):
    while True:
        start_id += 1
        yield start_id

class Account:
    transaction_id = transaction_id(100)

    def make_transaction(self):
        return next(Account.transaction_id)

a1 = Account()
a2 = Account()

print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())

import itertools

class Account:
    transaction_id = itertools.count(start=100, step=1)

    def make_transaction(self):
        return next(Account.transaction_id)

a1 = Account()
a2 = Account()

print(a1.make_transaction())
print(a2.make_transaction())
print(a1.make_transaction())

"""


    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.queryset.filter(
    #     serializer = self.serializer_class(queryset, many=True)
    #     return response.Response(serializer.data, status=status.HTTP_200_OK)

# history and insights
class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def get_serializer_class(self):
        if self.action == "provider_history":
            return TransactionProviderHistorySerializer
        if self.action == "seeker_history":
            return TransactionSeekerHistorySerializer

    def provider_history(self, *args, **kwargs):
        user = self.request.user
        queryset = self.queryset.filter(provider=user)
        if queryset:
            print("no value")
        serializer = self.get_serializer_class()(queryset, many=True)
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        # return response.Response(
        #     {"message":"No Data found" },
        #     status=status.HTTP_404_NOT_FOUND
        # )

    def seeker_history(self, *args, **kwargs):
        user = self.request.user
        queryset = self.queryset.filter(seeker=user)
        if queryset:
            print("no value")
        serializer = self.get_serializer_class()(queryset, many=True)
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        # return response.Response(
        #     {"message":"No Data found" },
        #     status=status.HTTP_404_NOT_FOUND
        # )
