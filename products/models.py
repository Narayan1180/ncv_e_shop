from django.db import models
from django.conf import settings
# Create your models here.

import uuid
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import (FileExtensionValidator, MaxValueValidator, MinValueValidator, ) 
from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Value
from django.utils.text import slugify
from datetime import datetime
MAX_IMAGE_SIZE_MB = 15


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def product_image_path(instance, filename):
    """Random filenames: avoids collisions, unsafe characters and guessable URLs."""
    ext = Path(filename).suffix.lower()
    return f"products/{uuid.uuid4().hex}{ext}"


def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Image must be smaller than {MAX_IMAGE_SIZE_MB} MB.")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        abstract = True
from django.utils.text import slugify


class Category(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)

    slug = models.SlugField( max_length=160, null=True, editable=False, unique=True)

    parent = models.ForeignKey( "self", on_delete=models.PROTECT, null=True, blank=True, related_name="children", )

    description = models.TextField(blank=True)

    image = models.ImageField( upload_to="categories/%Y/%m/", blank=True, null=True, )

    is_active = models.BooleanField( default=True, db_index=True,null=True )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

# --------------------------------------------------------------------------- #
# Manager / QuerySet
# --------------------------------------------------------------------------- #
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_final_price(self):
        """Annotate discounted price in the DB so you can filter/sort/aggregate on it."""
        return self.annotate(
            final_price=ExpressionWrapper(
                F("price") * (Value(100) - F("discount")) / Value(100),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
class Product(TimeStampedModel):
    name = models.CharField(max_length=250)
    seller=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="products",null=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True,editable=False)
    category = models.ForeignKey( "Category", on_delete=models.PROTECT,) # don't silently delete products with a category related_name="products", 
    description = models.TextField(blank=True)
    product_image = models.ImageField( upload_to=product_image_path, blank=True, null=True, validators=[ FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size, ], )
    price = models.DecimalField( max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))], )
    stock=models.PositiveIntegerField(default=0)
    discount = models.PositiveSmallIntegerField( default=0, validators=[MaxValueValidator(100)], help_text="Percentage discount (0-100).", )
    is_active = models.BooleanField(default=True, db_index=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "product"
        verbose_name_plural = "products"
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["name"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="product_price_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(discount__gte=0, discount__lte=100),
                name="product_discount_0_100",
            ),
        ]

    def __str__(self):
        return self.name

    # -- computed ----------------------------------------------------------- #
    @property
    def final_price(self):
        """Price after discount, rounded to 2 decimals."""
        value = self.price * (Decimal(100) - self.discount) / Decimal(100)
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def has_discount(self):
        return self.discount > 0

    # -- persistence -------------------------------------------------------- #
    def _generate_unique_slug(self):
        base = slugify(self.name)[:240] or "product"
        slug, n = base, 2
        qs = Product.objects.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

