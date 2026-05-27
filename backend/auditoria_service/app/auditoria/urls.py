from django.urls import path
from .views import LogAuditoriaListView, LogAuditoriaDetailView, health

urlpatterns = [
    path('auditoria/health/', health, name='auditoria-health'),
    path('auditoria/', LogAuditoriaListView.as_view(), name='auditoria-list'),
    path('auditoria/<uuid:id>/', LogAuditoriaDetailView.as_view(), name='auditoria-detail'),
]
