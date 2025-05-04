from django.conf import settings
from django.db import models
from product.models import ProductVariant
import uuid
import random
import string

# Generate unique order code like "YENE-2HF8K9LMQ7DT34WB"
def generate_order_code():
    return "YENE-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def generate_unique_order_code():
    while True:
        code = generate_order_code()
        if not Order.objects.filter(order_code=code).exists():
            return code

class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_half', 'Pending Half Payment'),
        ('half_paid', 'Half Paid'),  # Mark as half-paid when payment is confirmed
        ('awaiting_full', 'Awaiting Full Payment'),
        ('completed', 'Completed'),  # Mark as completed after full payment
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('bank', 'Bank'),
        ('telebirr', 'Telebirr'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_code = models.CharField(max_length=30, unique=True, default=generate_unique_order_code, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Track the payment method and amount once confirmed externally
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    delivery_eta_days = models.IntegerField()
    customer_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Use the custom user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # Guest info (if not logged in)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    guest_phone = models.CharField(max_length=20, null=True, blank=True)
    guest_city = models.CharField(max_length=100, null=True, blank=True)
    guest_address = models.TextField(null=True, blank=True)

    # Total price for the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_code} - {self.status} - {self.paid_amount or 0} {self.payment_method}"

    def save(self, *args, **kwargs):
        if self.user:
            self.guest_name = None
            self.guest_phone = None
            self.guest_city = None
            self.guest_address = None
        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_variant} - {self.total_price}"
