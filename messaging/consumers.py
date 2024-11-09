from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if not self.scope["user"].is_anonymous:
            await self.channel_layer.group_discard(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )

    async def notify(self, event):
        """Send notification to WebSocket"""
        await self.send_json(event["data"])

    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        command = content.get("command", None)
        if command == "get_unread_count":
            count = await self.get_unread_count()
            await self.send_json({
                "type": "unread_count",
                "count": count
            })

    @database_sync_to_async
    def get_unread_count(self):
        """Get unread message count for current user"""
        cache_key = f'unread_count_{self.scope["user"].id}'
        count = cache.get(cache_key)
        if count is None:
            from .models import MessageReadStatus
            count = MessageReadStatus.objects.filter(
                user=self.scope["user"],
                is_read=False
            ).count()
            cache.set(cache_key, count, 300)  # Cache for 5 minutes
        return count
