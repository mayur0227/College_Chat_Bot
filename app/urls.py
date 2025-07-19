from django.contrib import admin
from django.urls import path, include
from app import views
urlpatterns = [
    path("", views.index, name= "home"),
    path("log_in", views.log_in, name= "log_in"),
    path("register", views.register, name= "register"),
    path("dashboard", views.dashboard, name= "dashboard"),
    path("voice", views.voice, name= "voice"),
    path("forgot_password", views.forgot_password, name= "forgot_password"),
    path("log_out/", views.log_out, name= "log_out"),
    path("chat/<str:username>", views.chat, name= "chat_with_username"),
    path("chat", views.chat, name= "chat_without_username"),
    path('send_message/', views.send_message, name='send_message'),
    # path('voice-assistant/', views.voice_assistant, name='voice_assistant'),
    path('record_and_transcribe/', views.record_and_transcribe, name='record_and_transcribe'),
]

