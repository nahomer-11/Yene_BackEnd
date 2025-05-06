from rest_framework import serializers
from product.models import Product, ProductVariant, ProductVariantImage

class ProductVariantImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image_url', 'variant']
        read_only_fields = ['variant']

class ProductVariantAdminSerializer(serializers.ModelSerializer):
    images = ProductVariantImageAdminSerializer(many=True, required=False)

    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'color', 'size', 'extra_price', 'images']
        extra_kwargs = {'product': {'required': True}}

class ProductAdminSerializer(serializers.ModelSerializer):
    variants = ProductVariantAdminSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image_url', 'base_price', 'variants']

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
    
        # Create the main product first
        product = super().create(validated_data)
    
        # If no variants provided, create a default one
        if not variants_data:
            variants_data = [{
                "color": "Default",
                "size": "One Size",
                "extra_price": "0.00",
                "images": []
            }]
    
        # Create each variant and its images
        for variant_data in variants_data:
            images_data = variant_data.pop('images', [])
            variant = ProductVariant.objects.create(product=product, **variant_data)
            ProductVariantImage.objects.bulk_create([
                ProductVariantImage(product_variant=variant, **img_data)
                for img_data in images_data
            ])
    
        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', [])
        instance = super().update(instance, validated_data)
        
        existing_variants = {str(v.id): v for v in instance.variants.all()}
        
        # Update or create variants
        for variant_data in variants_data:
            variant_id = variant_data.get('id')
            images_data = variant_data.pop('images', [])
            
            if variant_id and str(variant_id) in existing_variants:
                variant = existing_variants[str(variant_id)]
                for attr, value in variant_data.items():
                    setattr(variant, attr, value)
                variant.save()
                
                # Update images
                variant.images.all().delete()
                ProductVariantImage.objects.bulk_create([
                    ProductVariantImage(product_variant=variant, **img_data)
                    for img_data in images_data
                ])
            else:
                new_variant = ProductVariant.objects.create(product=instance, **variant_data)
                ProductVariantImage.objects.bulk_create([
                    ProductVariantImage(product_variant=new_variant, **img_data)
                    for img_data in images_data
                ])
        
        # Delete removed variants
        kept_ids = [v.get('id') for v in variants_data if v.get('id')]
        instance.variants.exclude(id__in=kept_ids).delete()
        
        return instance
