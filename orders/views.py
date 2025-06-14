from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Order
from .serializers import OrderSerializer, OrderDetailSerializer
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'order_code'

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrderDetailSerializer  # ✅ include nested items
        return OrderSerializer  # ✅ for create/update

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user if request.user.is_authenticated else None
    
        # Guest validation
        if not user:
            required = ['guest_name', 'guest_phone', 'guest_city', 'guest_address']
            missing = [field for field in required if not data.get(field)]
            if missing:
                return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=400)
    
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=user)
    
        items = request.data.get('items', [])
        if not items:
            return Response({"detail": "No items provided"}, status=400)
    
        order_total = 0
    
        for item in items:
            try:
                variant = ProductVariant.objects.select_related('product').get(id=item['product_variant'])
            except ProductVariant.DoesNotExist:
                return Response({"detail": f"Variant {item['product_variant']} not found"}, status=400)
    
            quantity = item['quantity']
            unit_price = variant.product.base_price + variant.extra_price
            total_price = unit_price * quantity
            order_total += total_price
    
            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                quantity=quantity,
                price_per_unit=unit_price,
                total_price=total_price,
                product_name=variant.product.name,
                color=variant.color,
                size=variant.size,
                product_image=variant.images.first().image_url if variant.images.exists() else ''
            )
    
        order.total_price = order_total
        order.save()
    
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return Order.objects.none()

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response(
                {"detail": "Order not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )
