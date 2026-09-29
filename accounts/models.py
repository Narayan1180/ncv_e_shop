from django.contrib.auth.models import AbstractUser
from django.db import models


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class User(AbstractUser):

    class Role(models.TextChoices):

        CUSTOMER = "CUSTOMER", "Customer"
        SELLER = "SELLER", "Seller"
        ADMIN = "ADMIN", "Admin"

    username = None

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    role=models.CharField(max_length=20,choices=Role,default=Role.CUSTOMER,db_index=True,null=True,blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
