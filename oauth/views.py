import logging
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from kenar.models.chatmessage import SetNotifyChatPostConversationsRequest
from rest_framework.decorators import api_view

from addon.models import PostSession
from boilerplate import settings
from boilerplate.settings import kenar_app
from chat.models import ChatSession
from oauth.models import StateSession, TokenSession

logger = logging.getLogger(__name__)


@api_view(["GET"])
def oauth_callback(request):
    received_state = request.query_params.get("state")
    authorization_code = request.query_params.get("code")

    if not received_state or not authorization_code:
        return HttpResponseBadRequest("missing state or authorization code")

    try:
        state_session = StateSession.objects.get(state=received_state)

        try:
            access_token_response = kenar_app.oauth.get_access_token(authorization_code)

            token_session = TokenSession.objects.create(
                access_token=access_token_response.access_token,
                expires_in=timezone.now() + timedelta(seconds=access_token_response.expires_in),
            )

            if state_session.session_type == StateSession.Types.POST:
                post_session = PostSession.objects.get(oauth_state_session=state_session)
                post_session.oauth_token_session = token_session
                post_session.save()
                base_url = reverse("addon_app")
                query_string = urlencode({"state": state_session.state})
                url = f"{base_url}?{query_string}"
                return redirect(url)

            elif state_session.session_type == StateSession.Types.CHAT:
                chat_session = ChatSession.objects.get(oauth_state_session=state_session)
                chat_session.oauth_token_session = token_session
                chat_session.save()

                kenar_app.chat.set_notify_chat_post_conversations(
                    access_token=access_token_response.access_token,
                    data=SetNotifyChatPostConversationsRequest(
                        post_token=chat_session.post_token,
                        endpoint=settings.APP_BASE_URL + reverse("receive_notify"),
                        identification_key=str(chat_session.id),
                    ),
                )
                base_url = reverse("chat_app")
                query_string = urlencode({"state": state_session.state})
                url = f"{base_url}?{query_string}"
                return redirect(url)

        except httpx.HTTPStatusError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return HttpResponseServerError("Internal server error")
        except Exception as err:
            logger.error(f"An error occurred: {err}")
            return HttpResponseServerError("Internal server error")

    except StateSession.DoesNotExist:
        return HttpResponseBadRequest("Invalid state")
