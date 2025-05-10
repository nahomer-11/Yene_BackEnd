from rest_framework import serializers
from .models import Product, ProductVariant, ProductVariantImage, FeaturedCategory

class ProductVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['image_url', 'uploaded_at']



class ProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'base_price', 'variants']

    def get_variants(self, obj):
        # Return serialized variants if they exist, or an empty list
        variants = obj.variants.all()
        return ProductVariantSerializer(variants, many=True).data
        
class ProductVariantSerializer(serializers.ModelSerializer):
    images = ProductVariantImageSerializer(many=True, read_only=True)
    product = ProductSerializer(read_only=True)  # ✅ Add this line
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'extra_price', 'images', 'product']

class ProductDetailSerializer(ProductSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['variants']

class FeaturedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedCategory
        fields = ['title', 'description', 'image']
