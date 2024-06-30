import json
import logging
from urllib.parse import urlencode

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from kenar.app import Scope, SendChatMessageResourceIdParams
from kenar.models.oauth import OauthResourceType
from rest_framework.decorators import api_view

from boilerplate import settings
from boilerplate.settings import kenar_app
from chat.handler import ChatNotificationHandler, Notification, StartChatSessionRequest
from chat.models import ChatSession
from oauth.models import StateSession

logger = logging.getLogger(__name__)


@csrf_exempt
def start_chat_session(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or auth_header != settings.DIVAR_IDENTIFICATION_KEY:
        return HttpResponseForbidden("Unauthorized access")

    req_data = StartChatSessionRequest(**json.loads(request.body))

    post_token = req_data.post_token
    user_id = req_data.user_id
    peer_id = req_data.peer_id
    supplier_id = req_data.supplier.id
    demand_id = req_data.demand.id
    callback_url = req_data.callback_url

    # Needed for CHAT_POST_CONVERSATIONS_READ oauth scope
    if user_id != supplier_id:
        return HttpResponseForbidden("You must be post owner")

    existing_chat_session = ChatSession.objects.filter(
        post_token=post_token, supplier_id=supplier_id, demand_id=demand_id, oauth_token_session__isnull=False
    ).first()

    state_session = StateSession.objects.create(
        session_type=StateSession.Types.CHAT,
        callback_url=callback_url,
    )

    if existing_chat_session and not existing_chat_session.oauth_token_session.is_expired():
        if existing_chat_session.oauth_state_session:
            existing_chat_session.oauth_state_session.delete()
        existing_chat_session.oauth_state_session = state_session
        existing_chat_session.save()
        query_string = urlencode({"state": state_session.state})
        url = f"{settings.APP_BASE_URL + reverse('chat_app')}?{query_string}"
        return JsonResponse(
            {
                "status": "200",
                "message": "success",
                "url": url,
            }
        )

    chat_session = ChatSession.objects.create(
        post_token=post_token,
        user_id=user_id,
        peer_id=peer_id,
        supplier_id=supplier_id,
        demand_id=demand_id,
        oauth_state_session=state_session,
    )

    oauth_scopes = [
        Scope(
            resource_type=OauthResourceType.CHAT_MESSAGE_SEND,
            resource_id=kenar_app.oauth.get_send_message_resource_id(
                SendChatMessageResourceIdParams(user_id=user_id, peer_id=peer_id, post_token=post_token)
            ),
        ),
        Scope(resource_type=OauthResourceType.CHAT_POST_CONVERSATIONS_READ, resource_id=post_token),
    ]

    oauth_url = kenar_app.oauth.get_oauth_redirect(
        scopes=oauth_scopes,
        state=chat_session.oauth_state_session.state,
    )
    return JsonResponse({"status": "200", "message": "success", "url": oauth_url})


@api_view(["GET"])
def chat_app(request):
    state = request.query_params.get("state")
    if not state:
        return HttpResponseForbidden("permission denied")

    try:
        chat_session = ChatSession.objects.get(oauth_state_session_id=state)
    except ChatSession.DoesNotExist:
        return HttpResponseForbidden("permission denied")

    # TODO: Implement logic for after opening your application in chat
    # Example: Sending message in chat

    # After processing the chat logic, redirect to the callback URL
    callback_url = chat_session.oauth_state_session.callback_url

    # Delete the state session for security concerns
    chat_session.oauth_state_session.delete()

    return redirect(callback_url)


@api_view(["POST"])
def receive_notify(request):
    try:
        notification = Notification(**json.loads(request.body))
        handler = ChatNotificationHandler()
        handler.handle(notification)
    except Exception as e:
        logger.error(e)
        return JsonResponse(
            {
                "status": "500",
            }
        )

    return JsonResponse(
        {
            "status": "200",
        }
    )
