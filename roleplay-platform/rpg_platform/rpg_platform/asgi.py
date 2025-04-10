import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from rpg_platform.apps.messages.routing import websocket_urlpatterns as message_websocket_urlpatterns
from rpg_platform.apps.notifications.routing import websocket_urlpatterns as notification_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rpg_platform.rpg_platform.settings')

# Combine all WebSocket URL patterns
combined_websocket_urlpatterns = message_websocket_urlpatterns + notification_websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                combined_websocket_urlpatterns
            )
        )
    ),
})
