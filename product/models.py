from django.db import models
import uuid

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} - {self.id}'

class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  related_name='variants')
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f'{self.product.name} - {self.color} - {self.size}'

class ProductVariantImage(models.Model):
    variant = models.ForeignKey('product.ProductVariant', on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.variant.product.name} - {self.variant.color} - {self.variant.size} Image'
    
class FeaturedCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField() 

    def __str__(self):
        return self.title
