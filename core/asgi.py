import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django_asgi_app = get_asgi_application()

from web_socket.routing import websocket_urlpatterns
from web_socket.socket_middleware import QueryAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    # websocket

    # "websocket":
    #     URLRouter(websocket_urlpatterns)

    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))

    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
