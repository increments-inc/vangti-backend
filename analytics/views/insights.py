from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializers import *
from django.db.models import Avg, Sum, Count
from transactions.models import TransactionHistory
import calendar
from datetime import datetime, timedelta
from transactions.models import TransactionHistory

class InsightsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = InsightsSerializer
    http_method_names = ["get"]

    # def get_queryset(self):
    #     return self.queryset.filter(user=self.request.user)

    def profit_by_time(self, *args, **kwargs):
        # query_time = self.request.query_params.get("time")
        today = datetime.now()
        # if not query_time:
        #     return Response(
        #         "please provide query params - time",
        #         status=status.HTTP_204_NO_CONTENT,
        #     )
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
                print(stat)
                if stat["created_at"].day == date.day:
                    total_amount_of_transaction = stat["total_amount_of_transaction"]
                    profit = stat["profit"]
                    no_of_transaction = stat["no_of_transaction"]
                    break
            data = {
                "date": str(date.date().strftime("%m/%d/%Y")),
                "total_amount_of_transaction": str(total_amount_of_transaction),
                "profit": str(profit),
                "no_of_transaction": str(no_of_transaction),
            }
            scan_list.append(data)
        return Response(scan_list, status=status.HTTP_200_OK)

    def transaction_by_week(self, *args, **kwargs):
        today = datetime.now()
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

    # needs work
    def most_vangti(self, *args, **kwargs):
        today = datetime.now()
        data = {}
        note_list = list(TransactionHistory.objects.filter(
            created_at__lte=today,
            created_at__gte=today-timedelta(days=15), # check the options
            provider=self.request.user
        ).values_list("total_amount", flat=True))
        if len(note_list)==0:
            return Response("No data", status=status.HTTP_404_NOT_FOUND)
        return Response(max(note_list), status=status.HTTP_200_OK)
