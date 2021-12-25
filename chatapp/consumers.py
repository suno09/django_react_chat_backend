import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Message, UserChat


class ChatConsumer(WebsocketConsumer):

    def init_chat(self, data):
        username1 = data['username1']
        username2 = data['username2']
        user1 = UserChat.objects.get(user__username=username1)
        user2 = UserChat.objects.get(user__username=username2)
        content = {
            'command': 'init_chat'
        }
        if (not user1) or (not user2):
            content['error'] = 'Unable to get Users'
            self.send_message(content)
        content['success'] = 'Chatting in with success'
        self.send_message(content)

    def fetch_messages(self, data):
        username1 = data['username1']
        username2 = data['username2']

        messages = Message.last_50_messages(username1 + '_' + username2)
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        author = data['from']
        text = data['text']
        username1 = data['username1']
        username2 = data['username2']

        author_user, created = UserChat.objects.get_or_create(user=author)
        message = Message.objects.create(author=author_user,
                                         link=username1 + '_' + username2,
                                         content=text)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'id': str(message.id),
            'author': message.author.user.username,
            'content': message.content,
            'created_at': str(message.created_at)
        }

    commands = {
        'init_chat': init_chat,
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = 'room'
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # leave group room
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
