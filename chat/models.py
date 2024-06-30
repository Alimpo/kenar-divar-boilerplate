import uuid

from django.db import models

from oauth.models import StateSession, TokenSession


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_token = models.CharField(max_length=10)
    user_id = models.CharField(max_length=255)
    peer_id = models.CharField(max_length=255)
    supplier_id = models.CharField(max_length=255)
    demand_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    oauth_token_session = models.OneToOneField(TokenSession, on_delete=models.CASCADE, null=True, blank=True)
    oauth_state_session = models.OneToOneField(StateSession, on_delete=models.SET_NULL, null=True, blank=True)
