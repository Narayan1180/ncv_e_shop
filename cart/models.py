from django.db import models
from django.conf import settings
from products.models import Product
# Create your models here.

class Cart(models. Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)

    product = models.ForeignKey(Product,on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField()

#price = models.DecimalField( max_digits=10,decimal_places=2)



    