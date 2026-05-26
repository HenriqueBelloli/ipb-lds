from django.urls import path

from .views import(
    LogAuditoriaDetailView,
    LogAuditoriaListView
)

urlpatterns = [
    path('auditoria/', LogAuditoriaListView.as_view()),
    path('auditoria/<uuid:id>', LogAuditoriaDetailView.as_view())
]