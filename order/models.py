from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from products.models import Product




class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="orders")

    total_amount = models.DecimalField(max_digits=10,decimal_places=2)

    #status = models.CharField(max_length=20,default="pending")

    status = models.CharField(max_length=20,choices=[("pending", "Pending"),("confirmed", "Confirmed"),("cancelled", "Cancelled"),],default="pending")

    # Payment state
    payment_status = models.CharField(max_length=20,choices=[("pending", "Pending"),("paid", "Paid"),("failed", "Failed"),("refunded", "Refunded"),],default="pending")

    # Razorpay references
    razorpay_order_id = models.CharField(max_length=100,unique=True,null=True,blank=True)

    razorpay_payment_id = models.CharField(max_length=100,unique=True,null=True,blank=True)

    razorpay_signature = models.CharField(max_length=255,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True,null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")

    product = models.ForeignKey(Product,on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField()

    price = models.DecimalField( max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True,null=True)
    order_number = models.CharField(max_length=20, unique=True, null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_number:
            self.order_number = f"ORD-{self.id:06d}"
            super().save(update_fields=["order_number"])



class Notification(models.Model):

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", )

    channel = models.CharField( max_length=20, choices=Channel.choices, )

    recipient = models.CharField(max_length=255)

    message = models.TextField()

    subject = models.CharField( max_length=255, blank=True,)

    status = models.CharField( max_length=20, choices=Status.choices, default=Status.PENDING, )

    attempts = models.PositiveIntegerField(default=0)

    idempotency_key = models.CharField( max_length=255, unique=True, )

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField( null=True, blank=True, )

    failed_at = models.DateTimeField( null=True, blank=True, )

    def __str__(self):
        return f"{self.channel} - {self.recipient}"

