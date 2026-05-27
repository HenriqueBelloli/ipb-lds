from django.urls import path
from .views import (
    health,
    NotificationListView,
    NotificationDetailView,
    NotificationMarkAsReadView,
    NotificationMarkAllAsReadView,
)

urlpatterns = [
    path('notificacoes/health/', health, name='notification-health'),
    path('notificacoes/', NotificationListView.as_view()),
    path('notificacoes/ler-todas/', NotificationMarkAllAsReadView.as_view()),
    path('notificacoes/<uuid:id>/', NotificationDetailView.as_view()),
    path('notificacoes/<uuid:id>/ler/', NotificationMarkAsReadView.as_view()),
]
