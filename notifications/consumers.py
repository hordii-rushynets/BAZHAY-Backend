import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .message_text import welcome_message_uk, welcome_message_en


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')

        if self.user is None:
            await self.close(code=4001)
            return

        self.notifications_group = 'notifications_group'
        self.personal_group = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.notifications_group,
            self.channel_name
        )

        await self.channel_layer.group_add(
            self.personal_group,
            self.channel_name
        )

        await self.accept()

        if not self.user.is_already_registered:

            await self.channel_layer.group_send(
                self.personal_group,
                {
                    'type': 'send_notification',
                    'message': {
                        'welcome_message_uk': welcome_message_uk,
                        'welcome_message_en': welcome_message_en
                    }
                }
            )

            await database_sync_to_async(self.user.save)()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.notifications_group,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.personal_group,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')

        await self.channel_layer.group_send(
            self.notifications_group,
            {
                'type': 'send_notification',
                'message': message
            }
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))