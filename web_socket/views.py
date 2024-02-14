from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async


def vangti_request(request):
    message = {
        "seeker": "ajk",
    }
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "14-location-room", {
            'type': 'send_sdpt',
            'receive_dict': message,
        },
        # immediately=True
    )
    return JsonResponse({"message": message})



