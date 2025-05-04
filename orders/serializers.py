from rest_framework import serializers
from .models import Order, OrderItem
from product.models import ProductVariant
from product.serializers import ProductVariantSerializer
from django.db import transaction
from decimal import Decimal

class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['product_variant', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_code', 'status', 'payment_method', 'paid_amount', 'delivery_eta_days',
            'customer_note', 'guest_name', 'guest_phone', 'guest_city', 'guest_address',
            'items', 'total_price'
        ]
        read_only_fields = [
            'order_code', 'status', 'paid_amount', 'total_price', 'user'
        ]

    def get_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    @transaction.atomic
    def create(self, validated_data):
        items_data = self.initial_data.get('items', [])
        order = Order.objects.create(**validated_data)
        total_price = Decimal('0.00')

        for item_data in items_data:
            variant = ProductVariant.objects.get(id=item_data['product_variant'])
            quantity = item_data['quantity']
            price = variant.product.base_price + variant.extra_price
            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                quantity=quantity,
                price_per_unit=price,
                total_price=price * quantity
            )
            total_price += price * quantity

        order.total_price = total_price
        order.save()
        return order

    
