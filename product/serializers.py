from rest_framework import serializers
from .models import Product, ProductVariant, ProductVariantImage, FeaturedCategory

# ----------------------------- Variant Image
class ProductVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['image_url', 'uploaded_at']

# ----------------------------- Variant Public Serializer
class ProductVariantSerializer(serializers.ModelSerializer):
    images = ProductVariantImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'extra_price', 'images']

# ✅ ✅ ----------------------------- Variant Admin Serializer (to fix your error)
class ProductVariantImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image_url']

class ProductVariantAdminSerializer(serializers.ModelSerializer):
    images = ProductVariantImageAdminSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'extra_price', 'product', 'images']

# ----------------------------- Product
class ProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'base_price', 'variants']

    def get_variants(self, obj):
        variants = obj.variants.all()
        return ProductVariantSerializer(variants, many=True).data

# ----------------------------- Product Detail
class ProductDetailSerializer(ProductSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['variants']

# ----------------------------- Featured Category
class FeaturedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedCategory
        fields = ['title', 'description', 'image']
