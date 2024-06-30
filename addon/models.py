from django.db import models

from oauth.models import StateSession, TokenSession


class PostSession(models.Model):
    token = models.CharField(max_length=50)
    oauth_token_session = models.OneToOneField(TokenSession, on_delete=models.CASCADE, null=True, blank=True)
    oauth_state_session = models.OneToOneField(StateSession, on_delete=models.SET_NULL, null=True, blank=True)
