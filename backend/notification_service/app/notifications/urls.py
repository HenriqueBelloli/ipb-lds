from django.urls import path

from .views import(
    NotificationListView,
    NotificationDetailView,
)

urlpatterns = [
    path('notificacoes/', NotificationListView.as_view()),
    path('notificacoes/<uuid:id>/', NotificationDetailView.as_view()),
]