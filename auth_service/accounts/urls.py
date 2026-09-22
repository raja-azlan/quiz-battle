from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("profile/<int:user_id>/", views.profile),
    path("internal/update-stats/", views.update_stats),
]
