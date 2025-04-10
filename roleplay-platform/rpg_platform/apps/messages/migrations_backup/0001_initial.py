from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('characters', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='Room Name')),
                ('room_type', models.CharField(choices=[('private', 'Private'), ('group', 'Group')], default='private', max_length=10, verbose_name='Room Type')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('scene_description', models.TextField(blank=True, help_text='Setting and atmosphere for the current scene', verbose_name='Scene Description')),
                ('scene_background_color', models.CharField(blank=True, default='', max_length=20, verbose_name='Scene Background Color')),
                ('scene_image_url', models.URLField(blank=True, verbose_name='Scene Background Image')),
                ('scene_music_url', models.URLField(blank=True, verbose_name='Scene Background Music')),
                ('scene_intensity', models.PositiveSmallIntegerField(default=1, help_text='Intensity level from 1-5', verbose_name='Scene Intensity')),
                ('scene_status', models.CharField(choices=[('active', 'Active'), ('paused', 'Paused'), ('ooc', 'Out of Character'), ('break', 'Taking a Break')], default='active', max_length=20, verbose_name='Scene Status')),
                ('typing_effect_enabled', models.BooleanField(default=False, verbose_name='Enable Typing Effect')),
                ('message_timing_enabled', models.BooleanField(default=False, verbose_name='Enable Message Timing')),
                ('has_established_boundaries', models.BooleanField(default=False, verbose_name='Has Established Boundaries')),
                ('participants', models.ManyToManyField(related_name='chat_rooms', to='accounts.User', verbose_name='Participants')),
            ],
            options={
                'verbose_name': 'Chat Room',
                'verbose_name_plural': 'Chat Rooms',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('read', models.BooleanField(default=False, verbose_name='Read')),
                ('is_system_message', models.BooleanField(default=False, verbose_name='System Message')),
                ('is_ooc', models.BooleanField(default=False, verbose_name='Out of Character')),
                ('message_type', models.CharField(choices=[('regular', 'Regular'), ('whisper', 'Whisper'), ('action', 'Action'), ('thought', 'Thought'), ('narration', 'Narration')], default='regular', max_length=20, verbose_name='Message Type')),
                ('delay_seconds', models.PositiveSmallIntegerField(default=0, verbose_name='Delay Seconds')),
                ('character', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_messages', to='characters.Character', verbose_name='Character')),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat_messages.ChatRoom', verbose_name='Chat Room')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='accounts.User', verbose_name='Receiver')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='accounts.User', verbose_name='Sender')),
            ],
        ),
        migrations.CreateModel(
            name='DiceRoll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('formula', models.CharField(help_text='Format like "2d6+3" or "d20"', max_length=100, verbose_name='Dice Formula')),
                ('result', models.JSONField(help_text='JSON containing the dice roll results', verbose_name='Result')),
                ('total', models.IntegerField(verbose_name='Total Result')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('is_private', models.BooleanField(default=False, help_text='If true, only visible to GM and roller', verbose_name='Private Roll')),
                ('character', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dice_rolls', to='characters.Character', verbose_name='Character')),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dice_rolls', to='chat_messages.ChatRoom', verbose_name='Chat Room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dice_rolls', to='accounts.User', verbose_name='User')),
            ],
            options={
                'verbose_name': 'Dice Roll',
                'verbose_name_plural': 'Dice Rolls',
                'ordering': ['-created_at'],
            },
        ),
    ]
