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

    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='product_variant',
        required=True,
        write_only=True
    )

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    class Meta:
        model = OrderItem
        fields = ['variant_id', 'quantity'] 



# ✅ Used for create/update
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_code', 'status', 'total_price', 'paid_amount', 'payment_method', 'user','created_at', 'updated_at']


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
