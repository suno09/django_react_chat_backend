import uuid

from django.core.exceptions import ValidationError
from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone


def validate_message_content(content):
    if content is None or content == "" or content.isspace():
        raise ValidationError(
            'Content is empty/invalid',
            code='invalid',
            params={'content': content},
        )


class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        null=False,
        default=uuid.uuid4,
        editable=False
    )
    author = models.ForeignKey(
        'UserChat',
        blank=False,
        null=False,
        related_name='author_messages',
        on_delete=models.DO_NOTHING
    )
    link = models.TextField()
    content = models.TextField(validators=[validate_message_content])
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    @staticmethod
    def all_messages(link):
        try:
            return Message.objects.filter(link=link).order_by('-created_at')
        except Message.DoesNotExist:
            return []


class UserChat(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    last_read_date = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )
    online = models.BooleanField(null=False, blank=False, default=False)

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user.username

    def read(self):
        self.last_read_date = timezone.now()
        self.save()

    def unread_messages(self):
        return Message.objects.filter(created_at__gt=self.last_read_date) \
                              .count()
