from django.urls import path

from .views import(
    NotificationListView,
    NotificationDetailView,
    NotificationMarkAsReadView,
    NotificationMarkAllAsReadView
)

urlpatterns = [
    path('notificacoes/', NotificationListView.as_view()),
    path('notificacoes/<uuid:id>/', NotificationDetailView.as_view()),
    path('notificacoes/<uuid:id>/ler/', NotificationMarkAsReadView.as_view()),
    path('notificacoes/ler-todas/', NotificationMarkAllAsReadView.as_view()),
    
]