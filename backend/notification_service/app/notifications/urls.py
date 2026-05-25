from django.urls import path

from .views import(
    NotificationListView,
)

urlpatterns = [
    path('notificacoes/', NotificationListView.as_view()),
]