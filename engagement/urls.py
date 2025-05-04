from django.urls import path
from .views import (
    ReviewViewSet,
    AdminNotificationViewSet,
    UserHistoryViewSet
)

urlpatterns = [
    # Review URLs
    path('reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='review-list'),
    path('reviews/<uuid:pk>/', ReviewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='review-detail'),

    # Notification URLs
    path('notifications/', AdminNotificationViewSet.as_view({'get': 'list', 'post': 'create'}), name='notification-list'),
    path('notifications/<uuid:pk>/', AdminNotificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='notification-detail'),

    # User History URLs
    path('user-history/', UserHistoryViewSet.as_view({'get': 'list'}), name='user-history-list'),
    path('user-history/<uuid:pk>/', UserHistoryViewSet.as_view({'get': 'retrieve'}), name='user-history-detail'),
]
