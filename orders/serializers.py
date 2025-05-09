from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product, ProductVariant
from product.serializers import ProductVariantSerializer
from django.db import transaction
from decimal import Decimal

class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all(), required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)

    class Meta:
        model = OrderItem
        fields = ['product_variant', 'product', 'quantity']

    def validate(self, data):
        # Ensure at least one of `product_variant` or `product` is provided
        if not data.get('product_variant') and not data.get('product'):
            raise serializers.ValidationError("Either 'product_variant' or 'product' must be provided.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'order_code', 'status', 'payment_method', 'paid_amount', 'delivery_eta_days',
            'customer_note', 'guest_name', 'guest_phone', 'guest_city', 'guest_address',
            'items', 'total_price'
        ]
        read_only_fields = ['order_code', 'status', 'paid_amount', 'total_price', 'user']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = Decimal('0.00')

        for item_data in items_data:
            # Get either product_variant or product
            if item_data.get('product_variant'):
                variant = item_data['product_variant']
                price = variant.product.base_price + variant.extra_price
            elif item_data.get('product'):
                product = item_data['product']
                price = product.base_price  # Fallback to product price if variant is not provided
            else:
                raise serializers.ValidationError("Item must have either a product or product_variant.")

            quantity = item_data['quantity']
            OrderItem.objects.create(
                order=order,
                product_variant=item_data.get('product_variant'),
                product=item_data.get('product'),
                quantity=quantity,
                price_per_unit=price,
                total_price=price * quantity
            )
            total_price += price * quantity

        order.total_price = total_price
        order.save()
        return order
