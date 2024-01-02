from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializers import *
from django.db.models import Avg, Sum, Count
from transactions.models import TransactionHistory
# from .models import LocationRadius
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Q
import calendar
from datetime import datetime, timedelta


class InsightsViewSet(viewsets.ModelViewSet):
    queryset = Analytics.objects.all()
    serializer_class = InsightsSerializer
    http_method_names = ["get"]

    def get_serializer_class(self):

        return self.serializer_class

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def profit_by_time(self, *args, **kwargs):
        query_time = self.request.query_params.get("time")
        today = datetime.now()

        if not query_time:
            return Response(
                "please provide query params - time",
                status=status.HTTP_204_NO_CONTENT,
            )

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
        # branch_stat = list(
        #     self.get_queryset()
        #     .filter(
        #         created_at__month=today.month,
        #         created_at__year=today.year,
        #     )
        #     .values("total_order", "total_sale", "created_at__day")
        # )

        user_analytics = (
            self.get_queryset()
            .filter(
                created_at__month=today.month,
                created_at__year=today.year,
            )
            .values("no_of_transaction", "total_amount_of_transaction", "profit", "created_at")
        )

        serializer = self.serializer_class(user_analytics, many=True)
        scan_list = []

        # for date in day_s:
        #     orders = sales = 0
        #     for stat in branch_stat:
        #         if stat["created_at__day"] == date.day:
        #             sales = stat["total_sale"]
        #             orders = stat["total_order"]
        #             break
        #     data = {
        #         "date": str(date.date().strftime("%m/%d/%Y")),
        #         "total_order": str(orders),
        #         "total_sale": str(sales),
        #     }
        #     scan_list.append(data)
        # average_order = round(order_total/30, 0)
        return Response(serializer.data, status=status.HTTP_200_OK)
