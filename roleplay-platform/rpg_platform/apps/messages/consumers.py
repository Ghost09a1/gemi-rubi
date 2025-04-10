import json
import re
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import ChatRoom, ChatMessage, DiceRoll
from rpg_platform.apps.characters.models import Character

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat messages
    """
    async def connect(self):
        """
        Connect to the WebSocket and join the room group
        """
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Check if user is authenticated
        if self.user.is_anonymous:
            await self.close()
            return

        # Check if user is part of the room
        if not await self.is_room_participant():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify other users that this user connected
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_connect',
                'username': self.user.username,
                'user_id': self.user.id,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def disconnect(self, close_code):
        """
        Leave the room group on disconnect
        """
        # Notify other users that this user disconnected
        if hasattr(self, 'room_group_name') and hasattr(self, 'user') and not self.user.is_anonymous:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_disconnect',
                    'username': self.user.username,
                    'user_id': self.user.id,
                    'timestamp': timezone.now().isoformat(),
                }
            )

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = data.get('message', '')
            character_id = data.get('character_id')

            # Store message in database
            message_obj = await self.save_message(message, character_id)

            # Get character info
            character_info = None
            if message_obj.character:
                character = message_obj.character
                character_info = {
                    'id': character.id,
                    'name': character.name,
                    'image': await self.get_character_image(character)
                }

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_obj.id,
                    'message': message,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'character': character_info,
                    'timestamp': message_obj.created_at.isoformat(),
                }
            )
        elif message_type == 'dice_roll':
            # Handle dice roll
            formula = data.get('formula', '')
            character_id = data.get('character_id')
            is_private = data.get('is_private', False)

            # Parse and roll the dice
            dice_roll = await self.process_dice_roll(formula, character_id, is_private)

            if dice_roll:
                # Get character info
                character_info = None
                if dice_roll.character:
                    character = dice_roll.character
                    character_info = {
                        'id': character.id,
                        'name': character.name,
                        'image': await self.get_character_image(character)
                    }

                # Send dice roll result to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'dice_roll_result',
                        'roll_id': dice_roll.id,
                        'formula': dice_roll.formula,
                        'result': dice_roll.result,
                        'total': dice_roll.total,
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'character': character_info,
                        'timestamp': dice_roll.created_at.isoformat(),
                        'is_private': dice_roll.is_private
                    }
                )
        elif message_type == 'typing':
            # Send typing notification
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
        elif message_type == 'read_message':
            message_id = data.get('message_id')
            # Mark message as read
            await self.mark_message_read(message_id)

            # Send read receipt
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read',
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )

    async def chat_message(self, event):
        """
        Receive message from room group and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'character': event['character'],
            'timestamp': event['timestamp'],
        }))

    async def dice_roll_result(self, event):
        """
        Receive dice roll result from room group and send to WebSocket
        """
        # Only send private rolls to the roller or GMs
        if event['is_private'] and event['sender_id'] != self.user.id:
            # TODO: Check if user is a GM before filtering
            # For now, just show to the roller only
            return

        await self.send(text_data=json.dumps({
            'type': 'dice_roll_result',
            'roll_id': event['roll_id'],
            'formula': event['formula'],
            'result': event['result'],
            'total': event['total'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'character': event['character'],
            'timestamp': event['timestamp'],
            'is_private': event['is_private']
        }))

    async def user_typing(self, event):
        """
        Receive typing notification from room group and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def message_read(self, event):
        """
        Receive read receipt from room group and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def user_connect(self, event):
        """
        Receive user connect notification and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'user_connect',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    async def user_disconnect(self, event):
        """
        Receive user disconnect notification and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'user_disconnect',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def is_room_participant(self):
        """
        Check if the user is a participant in the chat room
        """
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def process_dice_roll(self, formula, character_id=None, is_private=False):
        """
        Process a dice roll formula, calculate results, and save to database

        Valid formulas:
        - Simple: d20, 2d6, d100
        - With modifiers: 2d6+3, d20-2, 3d8+5
        - Multiple dice: 2d6+1d8, d20+d4
        """
        try:
            # Get the chat room
            room = ChatRoom.objects.get(id=self.room_id)

            # Get character if provided
            character = None
            if character_id:
                try:
                    character = Character.objects.get(id=character_id, user=self.user)
                except Character.DoesNotExist:
                    pass

            # Parse the formula and calculate the result
            formula = formula.strip().lower()

            # Regular expressions for dice notation
            dice_pattern = r'(\d*)d(\d+)'
            modifier_pattern = r'([+-]\d+)'

            # Find all dice groups
            dice_groups = re.findall(dice_pattern, formula)

            # Find all modifiers
            modifiers = re.findall(modifier_pattern, formula)

            # Calculate total modifier value
            total_modifier = sum(int(mod) for mod in modifiers)

            # Process each dice group
            rolls = []
            for count, sides in dice_groups:
                # If no count specified, default to 1
                count = int(count) if count else 1
                sides = int(sides)

                # Roll the dice
                for _ in range(count):
                    roll = random.randint(1, sides)
                    rolls.append({
                        'sides': sides,
                        'value': roll
                    })

            # Calculate total
            total = sum(roll['value'] for roll in rolls) + total_modifier

            # Store results
            result = {
                'rolls': rolls,
                'modifiers': total_modifier
            }

            # Create the dice roll record
            dice_roll = DiceRoll.objects.create(
                chat_room=room,
                user=self.user,
                character=character,
                formula=formula,
                result=result,
                total=total,
                is_private=is_private
            )

            return dice_roll
        except Exception as e:
            print(f"Error processing dice roll: {e}")
            return None

    @database_sync_to_async
    def save_message(self, message_text, character_id):
        """
        Save a new message to the database
        """
        # Get the chat room
        room = ChatRoom.objects.get(id=self.room_id)

        # Get character if provided
        character = None
        if character_id:
            try:
                character = Character.objects.get(id=character_id, user=self.user)
            except Character.DoesNotExist:
                pass

        # Determine the receiver in a private chat
        if room.room_type == 'private' and room.participants.count() == 2:
            receiver = room.participants.exclude(id=self.user.id).first()
        else:
            # In group chats, there's no direct receiver
            # Store the sender as the receiver as a placeholder
            receiver = self.user

        # Create the message
        message = ChatMessage.objects.create(
            chat_room=room,
            sender=self.user,
            receiver=receiver,
            character=character,
            message=message_text
        )

        # Update room's updated_at timestamp
        room.save(update_fields=['updated_at'])

        return message

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """
        Mark a message as read
        """
        try:
            message = ChatMessage.objects.get(id=message_id, receiver=self.user)
            message.read = True
            message.save(update_fields=['read'])
            return True
        except ChatMessage.DoesNotExist:
            return False

    @database_sync_to_async
    def get_character_image(self, character):
        """
        Get the character's primary image URL
        """
        if character.has_images():
            image = character.get_primary_image()
            if image:
                return image.image.url
        return None
