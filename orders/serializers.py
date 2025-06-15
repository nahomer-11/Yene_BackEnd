from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product, ProductVariant
from product.serializers import ProductVariantAdminSerializer
from decimal import Decimal

# ✅ Used for create/update
class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(), required=False
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False
    )

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    class Meta:
        model = OrderItem
        fields = ['product_variant', 'product', 'quantity']

    def validate(self, data):
        if not data.get('product_variant') and not data.get('product'):
            raise serializers.ValidationError("Either 'product_variant' or 'product' must be provided.")
        return data


# ✅ Used for create/update
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            quantity = item_data.get("quantity", 1)
            product_variant = item_data.get("product_variant")
            product = item_data.get("product")

            if not product_variant:
                if not product:
                    raise serializers.ValidationError("Product ID is required if product_variant is not provided.")
                product_variant, _ = ProductVariant.objects.get_or_create(
                    product=product,
                    color="Default",
                    size="One Size",
                    defaults={"extra_price": Decimal('0.00')}
                )

            price = product_variant.product.base_price + (product_variant.extra_price or Decimal('0.00'))
            total_price = price * quantity

            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=quantity,
                price_per_unit=price,
                total_price=total_price
            )

        return order


# ✅ Used for GET (read-only): includes full nested product_variant
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantAdminSerializer(read_only=True)
    product_id = serializers.UUIDField(source='product_variant.product.id', read_only=True)
    variant_id = serializers.UUIDField(source='product_variant.id', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_variant', 'quantity', 'price_per_unit', 
            'total_price', 'product_name', 'color', 'size', 
            'product_image', 'product_id', 'variant_id'
        ]


# ✅ Used for GET (read-only): includes nested items
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    
    # Add status update validation
    def validate_status(self, value):
        valid_transitions = {
            'draft': ['pending_half', 'cancelled'],
            'pending_half': ['half_paid', 'cancelled'],
            'half_paid': ['awaiting_full', 'completed', 'cancelled'],
            'awaiting_full': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        
        current_status = self.instance.status if self.instance else None
        if current_status and value not in valid_transitions[current_status]:
            raise serializers.ValidationError(
                f"Invalid status transition from {current_status} to {value}"
            )
        return value
