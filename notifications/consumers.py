import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')

        if self.user is None:
            await self.close(code=4001)  # Закриваємо WebSocket якщо користувача немає
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

    async def disconnect(self, close_code):
        """
        Handle the disconnection of a WebSocket client.

        Removes the user from the notifications and personal groups.

        :param close_code: the code indicating the reason for disconnection.
        """
        await self.channel_layer.group_discard(
            self.notifications_group,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            self.personal_group,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive a message from the WebSocket.

        Sends the received message to the notifications group.

        :param text_data: the received message data as a string.
        """

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
        """
        Send a notification to the WebSocket client.

        :param event: the event containing the notification message.
        """
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
