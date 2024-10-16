from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from .serializers import CreditUser, AccumulatedCredits, AccumulatedCreditsSerializer


class AccumulatedCreditsViewSet(viewsets.ModelViewSet):
    queryset = AccumulatedCredits.objects.using('credits').all()
    serializer_class = AccumulatedCreditsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            try:
                user = CreditUser.objects.using('credits').get(user_uid=self.request.user.id)
            except CreditUser.DoesNotExist:
                user = CreditUser.objects.using('credits').create(user_uid=self.request.user.id)
            data = {
                "user": user.user_uid
            }
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        serializer = self.serializer_class(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
