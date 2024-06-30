from urllib.parse import urlencode

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from kenar.app import Scope
from kenar.models.oauth import OauthResourceType
from rest_framework.decorators import api_view

from addon.models import PostSession
from boilerplate import settings
from boilerplate.settings import kenar_app
from oauth.models import StateSession


@api_view(["GET"])
def start_post_session(request):
    post_token = request.query_params.get("post_token")
    callback_url = request.query_params.get("return_url")

    existing_post_session = PostSession.objects.filter(token=post_token, oauth_token_session__isnull=False).first()

    state_session = StateSession.objects.create(
        session_type=StateSession.Types.POST,
        callback_url=callback_url,
    )

    if existing_post_session and not existing_post_session.oauth_token_session.is_expired():
        if existing_post_session.oauth_state_session:
            existing_post_session.oauth_state_session.delete()
        existing_post_session.oauth_state_session = state_session
        existing_post_session.save()
        query_string = urlencode({"state": state_session.state})
        url = f"{settings.APP_BASE_URL + reverse('addon_app')}?{query_string}"
        return redirect(url)

    post_session = PostSession.objects.create(
        token=post_token,
        oauth_state_session=state_session,
    )

    oauth_scopes = [
        Scope(resource_type=OauthResourceType.USER_PHONE),
        Scope(resource_type=OauthResourceType.POST_ADDON_CREATE, resource_id=post_token),
    ]

    oauth_url = kenar_app.oauth.get_oauth_redirect(
        scopes=oauth_scopes,
        state=post_session.oauth_state_session.state,
    )

    return redirect(oauth_url)


@api_view(["GET"])
def addon_app(request):
    state = request.query_params.get("state")
    if not state:
        return HttpResponseForbidden("permission denied")

    try:
        post_session = PostSession.objects.get(oauth_state_session_id=state)
    except PostSession.DoesNotExist:
        return HttpResponseForbidden("permission denied")

    # TODO: Implement logic for after opening your application in post
    # Example: create post addon

    # After processing the post logic, redirect to the callback URL
    callback_url = post_session.oauth_state_session.callback_url

    # Delete the state session for security concerns
    post_session.oauth_state_session.delete()

    return redirect(callback_url)
