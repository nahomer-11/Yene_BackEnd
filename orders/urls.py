from django.urls import path
from .views import OrderViewSet 

urlpatterns = [
    # Order URLs
    path('', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),

    # Order Item URLs
    # path('items/', OrderItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='orderitem-list'),
    # path('items/<uuid:pk>/', OrderItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='orderitem-detail'),
]