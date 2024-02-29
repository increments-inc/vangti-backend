from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime, timedelta, time
from transactions.models import TransactionHistory
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from ..serializers import *
import random
from collections import Counter


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

    @extend_schema(
        parameters=[
            OpenApiParameter("interval", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
    )
    def profit_by_time(self, *args, **kwargs):
        interval = self.request.query_params.get("interval")
        if interval is None:
            return Response({"message": "no interval provided"}, status=status.HTTP_400_BAD_REQUEST)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        interval_day = 1
        date_list = ["0", "3", "6", "9", "12", "15", "18", "21"]
        scan_list = []

        if interval == "weekly":
            interval_day = 7
            date_list = [today - timedelta(days=x) for x in range(interval_day)]

        if interval == "monthly":
            interval_day = 30
            date_list = [today - timedelta(days=x) for x in range(interval_day)]

        user_analytics = self.queryset.filter(
            user=self.request.user,
            created_at__lte=datetime.now(),
            created_at__gte=today - timedelta(days=interval_day),
        ).values("no_of_transaction", "total_amount_of_transaction", "profit", "created_at")

        total_amount_of_transaction = profit = no_of_transaction = 0

        for date in date_list:
            # default
            total_amount_of_transaction = 0.0
            profit = 0.0
            no_of_transaction = 0
            # calculations
            rep_date = date
            if interval == "daily":
                hour = date
                date = time(hour=int(date))
                rep_date = today + timedelta(hours=int(hour))

            for stat in user_analytics:
                # default
                total_amount_of_transaction = 0.0
                profit = 0.0
                no_of_transaction = 0

                if interval != "daily":
                    if stat["created_at"].day == date.day:
                        total_amount_of_transaction = stat["total_amount_of_transaction"]
                        profit = stat["profit"]
                        no_of_transaction = stat["no_of_transaction"]
                        break
                else:
                    if (
                            date > stat["created_at"].time() >
                            (datetime.combine(datetime(1, 1, 1), date) - timedelta(
                                hours=3)).time()
                    ):
                        total_amount_of_transaction = stat["total_amount_of_transaction"]
                        profit = stat["profit"]
                        no_of_transaction = stat["no_of_transaction"]
                        break

            data = {
                "date": str(rep_date),
                "total_amount_of_transaction": float(total_amount_of_transaction),
                "profit": float(profit),
                "no_of_transaction": no_of_transaction,
            }
            # dev data
            # data = {
            #     "date": str(date),
            #     "total_amount_of_transaction": float(random.randint(10000, 500000)),
            #     "profit": float(random.randint(100, 5000)),
            #     "no_of_transaction": random.randint(100, 5000000),
            # }
            scan_list.append(data)
        return Response(scan_list, status=status.HTTP_200_OK)

    def transaction_by_week(self, *args, **kwargs):
        user_analytics = (
            self.queryset.filter(user=self.request.user,
                                       )
            .values("no_of_transaction", "total_amount_of_transaction", "profit", "created_at")
        )
        this_week = datetime.now() - timedelta(days=7)
        last_week = this_week - timedelta(days=7)
        this_week_trans = user_analytics.filter(
            created_at__gte=this_week
        )

        last_week_trans = user_analytics.filter(
            created_at__gte=last_week,
            created_at__lte=this_week
        )
        if not this_week_trans and not last_week_trans:
            data = {
                "no_of_transaction": 0,
                "total_amount_of_transaction": float(0),
                "amount_stat": float(0),
                "num_stat": float(0),
            }
            # dev data
            # data = {
            #     "no_of_transaction": 10000,
            #     "total_amount_of_transaction": float(200000),
            #     "amount_stat": float(10.99),
            #     "num_stat": float(-20.999),
            #
            # }
            return Response(data, status=status.HTTP_200_OK)

        this_week_trans_number = this_week_trans.aggregate(
            Sum("no_of_transaction", default=0),
            Sum("total_amount_of_transaction", default=0)
        )
        last_week_trans_number = last_week_trans.aggregate(
            Sum("no_of_transaction", default=0),
            Sum("total_amount_of_transaction", default=0)
        )
        print(this_week_trans_number, last_week_trans_number)
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
            "no_of_transaction": int(this_week_trans_number["no_of_transaction__sum"]),
            "total_amount_of_transaction": float(this_week_trans_number["total_amount_of_transaction__sum"]),
            "amount_stat": float(total_amount_transaction_stat),
            "num_stat": float(total_num_transaction_stat),
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
            return Response({"message": "no interval provided"}, status=status.HTTP_400_BAD_REQUEST)
        today = datetime.now()

        past_transactions = TransactionHistory.objects.filter(
            provider=self.request.user
        )

        interval_day = timedelta(hours=24)
        if interval == "weekly":
            interval_day = timedelta(days=7)
        if interval == "monthly":
            interval_day = timedelta(days=30)
        # revise
        note_list = list(past_transactions.filter(
            created_at__lte=today,
            created_at__gte=today - interval_day,
        ).values_list("total_amount", flat=True))

        # stat calculation
        this_note_list = past_transactions.filter(
            created_at__gte=today - interval_day,
        ).aggregate(
            Sum("total_amount", default=0)
        )

        past_note_list = past_transactions.filter(
            created_at__lte=today - interval_day,
            created_at__gte=today - interval_day*2,
        ).aggregate(
            Sum("total_amount", default=0)
        )

        print(this_note_list, past_note_list)
        try:
            print("here")
            stat = (
                           (
                                   this_note_list["total_amount__sum"] -
                                   past_note_list["total_amount__sum"]
                           ) /
                           (
                                   this_note_list["total_amount__sum"] +
                                   past_note_list["total_amount__sum"]
                           )
                   ) * 100
        except:
            stat = 0
        # print("demanded vangti",Counter(note_list).most_common(1))
        data = {
            "note": "0",
            "interval": interval,
            "stat": float(stat),
        }
        if len(note_list) != 0:
            data = {
                "note": str(Counter(note_list).most_common(1)[0][0]),
                "interval": interval,
                "stat": float(stat)
            }

        # dev data
        # data = {
        #     "note": "1000",
        #     "interval": interval,
        #     "stat": float(-10),
        # }
        return Response(data, status=status.HTTP_200_OK)
