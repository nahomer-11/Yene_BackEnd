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
    class Meta:
        model = Order
        fields = '__all__'  # or specify fields

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            quantity = item_data.get("quantity", 1)
            product_variant_id = item_data.get("product_variant")
            product_id = item_data.get("product")

            if product_variant_id:
                product_variant = ProductVariant.objects.get(id=product_variant_id)
            else:
                if not product_id:
                    raise serializers.ValidationError("Product ID is required if product_variant is not provided.")

                product = Product.objects.get(id=product_id)
                # Get or create default variant for this product
                product_variant, _ = ProductVariant.objects.get_or_create(
                    product=product,
                    name="Default",
                    defaults={"extra_price": 0.00}
                )

            price = product_variant.product.price + (product_variant.extra_price or 0)
            total_price = price * quantity

            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=quantity,
                price_per_unit=price,
                total_price=total_price
            )

        return order
