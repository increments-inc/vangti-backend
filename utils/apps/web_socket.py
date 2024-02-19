from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_message_to_channel(request, user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"{user.id}-room",
        {
            "type": "send_to_receiver_data",
            'receive_dict': message
        }
    )
    return
