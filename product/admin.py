from django.contrib import admin
from .models import Product, ProductVariant, ProductVariantImage, FeaturedCategory
# Register your models here.
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductVariantImage)
admin.site.register(FeaturedCategory)