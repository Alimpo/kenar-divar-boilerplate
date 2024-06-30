import uuid

from django.db import models
from django.utils.timezone import now


class StateSession(models.Model):
    class Types(models.TextChoices):
        CHAT = "CHAT", "Chat"
        POST = "POST", "Post"

    state = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_type = models.CharField(max_length=10, choices=Types.choices)
    callback_url = models.URLField()
    created_at = models.DateTimeField(default=now)


class TokenSession(models.Model):
    access_token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    expires_in = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return now() >= self.expires_in
