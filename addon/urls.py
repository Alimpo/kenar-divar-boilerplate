from django.urls import path

from . import views

urlpatterns = [
    path("start_post_session/", views.start_post_session, name="start_app"),
    path("", views.addon_app, name="addon_app"),
]
