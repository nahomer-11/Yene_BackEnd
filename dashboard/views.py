from rest_framework import viewsets, permissions
from product.models import Product, ProductVariant, ProductVariantImage
from orders.models import Order
from orders.serializers import OrderSerializer  # Critical import added
from dashboard.serializers import (
    ProductAdminSerializer,
    ProductVariantAdminSerializer,
    ProductVariantImageAdminSerializer
)
from user.models import User
from user.serializers import UserSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

# -------------------- Product Admin --------------------
class ProductAdminViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('variants__images')
    serializer_class = ProductAdminSerializer
    permission_classes = [IsAdminUser]

class ProductVariantAdminViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product').prefetch_related('images')
    serializer_class = ProductVariantAdminSerializer
    permission_classes = [IsAdminUser]

class ProductVariantImageAdminViewSet(viewsets.ModelViewSet):
    queryset = ProductVariantImage.objects.select_related('variant')
    serializer_class = ProductVariantImageAdminSerializer
    permission_classes = [IsAdminUser]

# -------------------- Order Admin --------------------

class OrderAdminViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        'items__product_variant__product'
    )
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'order_code'

# -------------------- Registered User Admin --------------------
class RegisteredUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]