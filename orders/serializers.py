from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product, ProductVariant
from product.serializers import ProductVariantAdminSerializer
from decimal import Decimal

# ✅ Used for create/update
class OrderCreateSerializer(serializers.Serializer):
    """
    Simplified serializer for order creation
    Doesn't use model-based serialization to avoid conflicts
    """
    delivery_eta_days = serializers.IntegerField()
    customer_note = serializers.CharField(required=False, allow_blank=True)
    guest_name = serializers.CharField()
    guest_phone = serializers.CharField()
    guest_city = serializers.CharField()
    guest_address = serializers.CharField()
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of order items with variant_id and quantity"
    )

class OrderItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
