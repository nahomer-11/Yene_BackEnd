from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderDetailSerializer
from product.models import ProductVariant 
from django.http import Http404
import logging
from django.db import transaction
from django.core.cache import cache


logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'order_code'

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrderDetailSerializer
        return OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user if request.user.is_authenticated else None
        
        # Guest validation
        if not user:
            required = ['guest_name', 'guest_phone', 'guest_city', 'guest_address']
            missing = [field for field in required if not data.get(field)]
            if missing:
                return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=400)
        
        # Validate items exist
        if 'items' not in data or not data['items']:
            return Response({"detail": "No items provided"}, status=400)
        
        # Use serializer for order-level validation
        order_serializer = self.get_serializer(data=data)
        order_serializer.is_valid(raise_exception=True)
        
        # Extract and validate items
        items_data = data.get('items', [])
        variant_ids = [item.get('variant_id') for item in items_data]
        
        # Validate all items have variant_ids
        if any(vid is None for vid in variant_ids):
            return Response({"detail": "All items must have a variant_id"}, status=400)
        
        try:
            # Fetch variants in bulk
            variants = ProductVariant.objects.select_related('product').prefetch_related(
                'images'
            ).in_bulk(variant_ids)
        except Exception as e:
            logger.error(f"Variant lookup error: {str(e)}")
            return Response({"detail": "Error processing items"}, status=400)
        
        # Validate all variants exist
        missing_ids = [vid for vid in variant_ids if vid not in variants]
        if missing_ids:
            return Response({
                "detail": f"Variants not found: {', '.join(missing_ids)}"
            }, status=400)

        with transaction.atomic():
            # Create order instance
            order = Order.objects.create(
                user=user,
                delivery_eta_days=data.get('delivery_eta_days'),
                customer_note=data.get('customer_note', ''),
                guest_name=data.get('guest_name'),
                guest_phone=data.get('guest_phone'),
                guest_city=data.get('guest_city'),
                guest_address=data.get('guest_address'),
                status='draft'
            )
            
            order_items = []
            order_total = Decimal('0.00')
            
            for item in items_data:
                variant = variants[item['variant_id']]
                quantity = int(item['quantity'])
                unit_price = variant.product.base_price + (variant.extra_price or Decimal('0.00'))
                total_price = unit_price * quantity
                order_total += total_price
                
                # Get first image if exists
                first_image = variant.images.first()
                
                order_items.append(OrderItem(
                    order=order,
                    product_variant=variant,
                    quantity=quantity,
                    price_per_unit=unit_price,
                    total_price=total_price,
                    product_name=variant.product.name,
                    color=variant.color,
                    size=variant.size,
                    product_image=first_image.image_url if first_image else '',
                    product_id=variant.product.id
                ))
            
            # Bulk create items
            OrderItem.objects.bulk_create(order_items)
            order.total_price = order_total
            order.save()
        
        # Return detailed response
        response_serializer = OrderDetailSerializer(order)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=201, headers=headers)

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
