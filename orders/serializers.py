from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product, ProductVariant
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

        for idx, item_data in enumerate(items_data, start=1):
            quantity = item_data.get('quantity', 1)

            product_variant_id = item_data.get('product_variant')
            product_id = item_data.get('product')

            if product_variant_id:
                try:
                    variant = ProductVariant.objects.select_related('product').get(id=product_variant_id)
                except ProductVariant.DoesNotExist:
                    raise serializers.ValidationError(
                        {f"items": [f"Item {idx}: Product variant with ID {product_variant_id} not found."]}
                    )
                price = variant.product.base_price + variant.extra_price
                product_variant = variant

            elif product_id:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        {f"items": [f"Item {idx}: Product with ID {product_id} not found."]}
                    )

                if product.variants.exists():
                    raise serializers.ValidationError(
                        {f"items": [f"Item {idx}: Product ID {product_id} has variants. Use 'product_variant' instead."]}
                    )

                price = product.base_price
                product_variant = None

            else:
                raise serializers.ValidationError(
                    {f"items": [f"Item {idx}: Either 'product_variant' or 'product' is required."]}
                )

            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=quantity,
                price_per_unit=price,
                total_price=price * quantity
            )
            total_price += price * quantity

        order.total_price = total_price
        order.save()
        return order
