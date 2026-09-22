from django.urls import path

from . import views

urlpatterns = [
    path("rooms/", views.create_room),
    path("rooms/<str:code>/", views.room_detail),
    path("rooms/<str:code>/join/", views.join_room),
    path("rooms/<str:code>/questions/", views.room_questions),
    path("rooms/<str:code>/answer/", views.submit_answer),
]
