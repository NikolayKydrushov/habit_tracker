from django.urls import path
from . import views

urlpatterns = [
    path("link/", views.LinkTelegramView.as_view(), name="link_telegram"),
    path("profile/", views.TelegramProfileView.as_view(), name="telegram_profile"),
    path("unlink/", views.UnlinkTelegramView.as_view(), name="unlink_telegram"),
]
