from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.healthcheck, name="healthcheck"),
    path("profile/", views.profile_detail, name="profile_detail"),
    path("messages/", views.message_create, name="message_create"),
    path("ai-chat/", views.ai_chat, name="ai_chat"),
    path("chat-history/<str:session_id>/", views.chat_history, name="chat_history"),
]
