from rest_framework import viewsets, permissions
from product.models import Product, ProductVariant, ProductVariantImage
from orders.models import Order
from orders.serializers import OrderSerializer, OrderDetailSerializer
from dashboard.serializers import (
    ProductAdminSerializer,
    ProductVariantAdminSerializer,
    ProductVariantImageAdminSerializer
)
from user.models import User
from user.serializers import UserSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

# Product admin endpoints
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

# ✅ Updated to return nested variant info in detail endpoint
class OrderAdminViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items').select_related('user').order_by('-created_at')
    permission_classes = [IsAdminUser]
    lookup_field = 'order_code'

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        
        # Validate status transition
        valid_transitions = {
            'draft': ['pending_half', 'cancelled'],
            'pending_half': ['half_paid', 'cancelled'],
            'half_paid': ['awaiting_full', 'completed', 'cancelled'],
            'awaiting_full': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        
        if new_status and new_status not in valid_transitions[order.status]:
            return Response(
                {"detail": f"Invalid status transition from {order.status} to {new_status}"},
                status=400
            )
        
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer

# Registered users listing (admin only)
class RegisteredUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
