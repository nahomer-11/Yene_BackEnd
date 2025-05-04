from django.urls import path
from . import views

urlpatterns = [
    # Product Admin Views
    path('yene_admin/products/', views.ProductAdminViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('yene_admin/products/<uuid:pk>/', views.ProductAdminViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='product-detail'),
    
    path('yene_admin/product-variants/', views.ProductVariantAdminViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-variant-list'),
    path('yene_admin/product-variants/<uuid:pk>/', views.ProductVariantAdminViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='product-variant-detail'),
    
    path('yene_admin/product-variant-images/', views.ProductVariantImageAdminViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-variant-image-list'),
    path('yene_admin/product-variant-images/<uuid:pk>/', views.ProductVariantImageAdminViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='product-variant-image-detail'),
    
    # Order Admin Views
    path('yene_admin/orders/', views.OrderAdminViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('yene_admin/orders/<str:order_code>/', views.OrderAdminViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='order-detail'),
    
    # Registered User Admin Views
    path('yene_admin/users/', views.RegisteredUserViewSet.as_view({'get': 'list'}), name='user-list'),
    path('yene_admin/users/<uuid:pk>/', views.RegisteredUserViewSet.as_view({'get': 'retrieve'}), name='user-detail'),
]
