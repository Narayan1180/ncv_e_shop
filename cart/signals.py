from django.db.models.signals import pre_save,post_delete
from django.dispatch import receiver
from .models import Cart

@receiver(pre_save, sender=Cart)
def product_pre_save(sender, instance, **kwargs):
    print("Before Creating the cart....")


@receiver(post_delete, sender=Cart)
def product_pre_save(sender, instance, **kwargs):
    print("After delete....")

