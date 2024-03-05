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
from utils.custom_pagination import CustomPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from ..serializers import *
from django.db.models import Q
from utils.apps.transaction import get_transaction_id
from utils.apps.web_socket import send_message_to_channel
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from analytics.models import UserRating, UserSeekerRating
from ..tasks import send_out_location_data


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().select_related(
        "seeker__user_info", "provider__user_info","provider__userrating_user", "seeker__userrating_user"
    )
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_no'
    http_method_names = ["get", "patch", "delete"]

    def get_serializer_class(self):
        if self.action == "update_provider":
            return TransactionProviderSerializer
        if self.action == "update_seeker":
            return TransactionSeekerSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        # no list shown
        queryset = self.queryset.filter(Q(seeker=request.user) | Q(provider=request.user))
        serializer = self.serializer_class(queryset, many=True, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # print(kwargs)
        transaction_id = get_transaction_id(kwargs[self.lookup_field])

        # transaction_id = self.get_object(pk=transaction_id)
        try:
            instance = self.queryset.get(id=int(transaction_id))
            print("check instance transcation   ",instance)
        except:
            return response.Response({"errors": "No transaction instance found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user not in [instance.provider, instance.seeker]:
            return response.Response({"errors": "User not authorised"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(instance, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return response.Response("", status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                examples=[
                ],
            ),
        }
    )
    def destroy(self, request, *args, **kwargs):
        transaction_id = get_transaction_id(kwargs[self.lookup_field])
        try:
            instance = self.queryset.get(id=int(transaction_id))
        except:
            return response.Response({"errors": "No transaction instance found"}, status=status.HTTP_404_NOT_FOUND)
        if instance.is_completed:
            return response.Response({"errors": "Completed transactions cannot be deleted"}, status=status.HTTP_400_BAD_REQUEST)
        # serializer = self.serializer_class(instance, context={"request": request})
        if request.user not in [instance.provider, instance.seeker]:
            return response.Response({"errors": "User not authorised"}, status=status.HTTP_403_FORBIDDEN)
        try:
            message = {
                "request": "TRANSACTION",
                "status": "CANCELLED",
                'data': {
                    'amount': int(instance.total_amount),
                    'preferred': instance.preferred_notes,
                    'transaction_id': instance.get_transaction_unique_no,
                    'seeker': f'{instance.seeker.id}',
                    'seeker_info': {
                        'name': '',
                        'picture': {'url': '', 'hash': ''},
                        'rating': 0.0,
                        'total_deals': 0
                    },
                    'provider': f'{instance.provider.id}'
                }
            }
            # for i in range(3):
            send_message_to_channel(request, instance.seeker, message)
            send_message_to_channel(request, instance.provider, message)

            # keep in Cancelled transaction
            CancelledTransaction.objects.create(
                transaction=kwargs[self.lookup_field],
                provider=instance.provider,
                seeker=instance.seeker,
                total_amount=instance.total_amount,
                preferred_notes=instance.preferred_notes
            )
            # calculations for rating
            total_cancelled = CancelledTransaction.objects.filter(
                provider=instance.provider
            ).count()
            total_success = TransactionHistory.objects.filter(
                provider=instance.provider
            ).count()
            deal_success_rate = (total_success / (total_success + total_cancelled)) * 100
            user_rating = UserRating.objects.get(
                user=instance.provider
            )
            user_rating.deal_success_rate = deal_success_rate
            user_rating.dislikes = total_cancelled
            user_rating.save()

            # calculations for seeker rating
            total_cancelled = CancelledTransaction.objects.filter(
                seeker=instance.seeker
            ).count()
            total_success = TransactionHistory.objects.filter(
                seeker=instance.seeker
            ).count()
            deal_success_rate = (total_success / (total_success + total_cancelled)) * 100
            try:
                user_rating = UserSeekerRating.objects.get(
                    user=instance.seeker
                )
                user_rating.deal_success_rate = deal_success_rate
                user_rating.dislikes = total_cancelled
                user_rating.save()
            except UserSeekerRating.DoesNotExist:
                UserSeekerRating.objects.create(
                    user=instance.seeker,
                    deal_success_rate=deal_success_rate,
                    dislikes=total_cancelled
                )

            # destroy action
            self.perform_destroy(instance)
            return response.Response({"detail": "transaction instance deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response({"errors": f"{e}, transaction could not be deleted"},
                                     status=status.HTTP_400_BAD_REQUEST)

    def update_seeker(self, request, *args, **kwargs):
        print(request.data)
        try:
            transaction_id = get_transaction_id(request.data["transaction_no"])
            instance = self.queryset.get(id=int(transaction_id))
        except:
            return response.Response({"errors": "No transaction instance found"}, status=status.HTTP_404_NOT_FOUND)
        print(instance.is_completed)
        if instance.is_completed:
            return response.Response({"errors": "Deal is already completed"}, status=status.HTTP_400_BAD_REQUEST)
        if instance.seeker == request.user:
            serializer = self.get_serializer_class()(
                instance, context={"request": request},
                data=request.data,
                partial=True)
            if serializer.is_valid():
                instance = serializer.save()

                if instance == -1:
                    return response.Response({"errors": "transaction pin not valid"},
                                             status=status.HTTP_400_BAD_REQUEST)

                # transaction
                message = {
                    'request': 'TRANSACTION',
                    'status': 'COMPLETED_TRANSACTION',
                    'data': {
                        'amount': int(instance.total_amount),
                        'preferred': instance.preferred_notes,
                        'transaction_id': instance.get_transaction_unique_no,
                        'seeker': f'{instance.seeker.id}',
                        'seeker_info': {
                            'name': '',
                            'picture': {'url': '', 'hash': ''},
                            'rating': 0.0,
                            'total_deals': 0
                        },
                        'provider': f'{instance.provider.id}'
                    }
                }
                send_message_to_channel(request, instance.provider, message)

                # Location
                message = {
                    'request': 'LOCATION',
                    'status': 'COMPLETED_TRANSACTION',
                    'data': None
                }
                send_message_to_channel(request, instance.provider, message)
                send_message_to_channel(request, instance.seeker, message)


                total_cancelled = CancelledTransaction.objects.filter(
                    provider=instance.provider
                ).count()
                total_success = TransactionHistory.objects.filter(
                    provider=instance.provider
                ).count()
                deal_success_rate = (total_success / (total_success + total_cancelled)) * 100
                user_rating = UserRating.objects.get(
                    user=instance.provider
                )
                user_rating.deal_success_rate = deal_success_rate
                user_rating.save()

                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response({"errors": "data not valid"}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response({"message": "not authorised to update"}, status=status.HTTP_403_FORBIDDEN)

    def update_provider(self, request, *args, **kwargs):
        transaction_id = get_transaction_id(request.data["transaction_no"])
        try:
            instance = self.queryset.get(id=int(transaction_id))
        except:
            return response.Response({"errors": "No transaction instance found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user == instance.provider:
            serializer = self.get_serializer_class()(instance, context={"request": request}, data=request.data,
                                                     partial=True)
            if serializer.is_valid():
                data_instance = serializer.save()
                data = self.serializer_class(data_instance, context={"request": request}).data
                return response.Response(data, status=status.HTTP_200_OK)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response({"message": "not authorised to update"}, status=status.HTTP_403_FORBIDDEN)

    def open_transactions(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            Q(seeker=request.user) | Q(provider=request.user)
        ).filter(
            is_completed=False
        )
        if queryset.exists():
            instance = queryset.order_by("-created_at").first()
            serializer = self.serializer_class(instance, context={"request": request})
            if instance:
                print("here in transaction id", instance.id)
                # transaction_id = get_transaction_id(instance.id)
                send_out_location_data.delay(request.user.id, instance.id)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response({}, status=status.HTTP_200_OK)


# history and insights
class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all().select_related("seeker__user_info", "provider__user_info", "provider__userrating_user", "seeker__userrating_user")
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    # pagination_class = CustomPagination

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
        serializer = self.get_serializer_class()(queryset, many=True, context={"request": self.request})

        page = self.paginate_queryset(queryset)
        print(page)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        # data = self.get_paginated_response(serializer.data)
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
        serializer = self.get_serializer_class()(queryset, many=True, context={"request": self.request})
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        # data = self.get_paginated_response(serializer.data)
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        # return response.Response(
        #     {"message":"No Data found" },
        #     status=status.HTTP_404_NOT_FOUND
        # )
