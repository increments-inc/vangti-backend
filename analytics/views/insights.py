from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from ..serializers import *
from django.db.models import Avg, Sum, Count
import calendar
from datetime import datetime, timedelta
from transactions.models import TransactionHistory
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter, OpenApiTypes


class InsightsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = InsightsListSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def get_serializer_class(self):
        if self.action == "most_vangti":
            return DemandedVangtiSerializer
        if self.action == "transaction_by_week":
            return AvgTransactionSerializer
        return InsightsListSerializer

    def profit_by_time(self, *args, **kwargs):
        today = datetime.now()
        try:
            num_days = calendar.monthrange(today.year, today.month)[1]
            day_s = [
                datetime(today.year, today.month, day)
                for day in range(1, num_days + 1)
            ]
        except:
            return Response(
                {"detail": "Please Provide Query Params"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_analytics = (
            self.get_queryset()
            .filter(
                created_at__month=today.month,
                created_at__year=today.year,
            )
            .values("no_of_transaction", "total_amount_of_transaction", "profit", "created_at")
        )
        print(user_analytics)
        serializer = self.serializer_class(user_analytics, many=True)
        scan_list = []

        for date in day_s:
            total_amount_of_transaction = profit = no_of_transaction = 0
            for stat in user_analytics:
                # print(stat)
                if stat["created_at"].day == date.day:
                    total_amount_of_transaction = stat["total_amount_of_transaction"]
                    profit = stat["profit"]
                    no_of_transaction = stat["no_of_transaction"]
                    break
            data = {
                "date": str(date.date().strftime("%m/%d/%Y")),
                "total_amount_of_transaction": total_amount_of_transaction,
                "profit": profit,
                "no_of_transaction": no_of_transaction,
            }
            scan_list.append(data)
        return Response(scan_list, status=status.HTTP_200_OK)

    def transaction_by_week(self, *args, **kwargs):
        user_analytics = (
            self.get_queryset()
            .values("no_of_transaction", "total_amount_of_transaction", "profit", "created_at")
        )
        print(user_analytics)
        this_week = datetime.now() - timedelta(days=7)
        last_week = this_week - timedelta(days=7)
        this_week_trans = user_analytics.filter(
            created_at__gte=this_week
        )

        last_week_trans = user_analytics.filter(
            created_at__gte=last_week,
            created_at__lte=this_week
        )

        print(this_week_trans, last_week_trans)
        print(this_week, last_week)
        scan_list = []
        this_week_trans_number = this_week_trans.aggregate(
            Sum("no_of_transaction", default=0),
            Sum("total_amount_of_transaction", default=0)
        )
        last_week_trans_number = last_week_trans.aggregate(
            Sum("no_of_transaction", default=0),
            Sum("total_amount_of_transaction", default=0)
        )
        print(this_week_trans_number, last_week_trans_number)
        if this_week_trans_number["no_of_transaction__sum"] == 0 and last_week_trans_number["no_of_transaction__sum"] == 0:
            data = {
                "total_amount_of_transaction": 0,
                "no_of_transaction": 0,
                "amount_stat": str(0),
                "num_stat": str(0),

            }
            return Response(data, status=status.HTTP_200_OK)
        total_amount_transaction_stat = (
                                                (
                                                        this_week_trans_number["total_amount_of_transaction__sum"] -
                                                        last_week_trans_number["total_amount_of_transaction__sum"]
                                                ) /
                                                (
                                                        this_week_trans_number["total_amount_of_transaction__sum"] +
                                                        last_week_trans_number["total_amount_of_transaction__sum"]
                                                )
                                        ) * 100

        total_num_transaction_stat = (
                                             (
                                                     this_week_trans_number["no_of_transaction__sum"] -
                                                     last_week_trans_number["no_of_transaction__sum"]
                                             ) /
                                             (
                                                     this_week_trans_number["no_of_transaction__sum"] +
                                                     last_week_trans_number["no_of_transaction__sum"]
                                             )
                                     ) * 100

        data = {
            "total_amount_of_transaction": this_week_trans_number["total_amount_of_transaction__sum"],
            "no_of_transaction": this_week_trans_number["no_of_transaction__sum"],
            "amount_stat": str(total_amount_transaction_stat),
            "num_stat": str(total_num_transaction_stat),

        }
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter("interval", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
    )
    def most_vangti(self, *args, **kwargs):
        interval = self.request.query_params.get("interval")
        note_list = "0"
        if interval is None:
            return Response({
                "message": "no interval provided"
            }, status=status.HTTP_400_BAD_REQUEST)
        today = datetime.now()
        past_transactions = TransactionHistory.objects.filter(
            created_at__lte=today,
            provider=self.request.user
        )

        if interval == "daily":
            note_list = list(past_transactions.filter(
                created_at__gte=today - timedelta(days=1),
            ).values_list("total_amount", flat=True))
        if interval == "weekly":
            note_list = list(past_transactions.filter(
                created_at__gte=today - timedelta(days=7),
            ).values_list("total_amount", flat=True))
        if interval == "monthly":
            note_list = list(past_transactions.filter(
                created_at__gte=today - timedelta(days=30),
            ).values_list("total_amount", flat=True))

        if len(note_list) != 0:
            return Response({
                "note": max(note_list),
                "interval": interval
            }, status=status.HTTP_200_OK)
        return Response({"message": "no data"}, status=status.HTTP_404_NOT_FOUND)
