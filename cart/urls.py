
from django.contrib import admin
from django.urls import path,include
from .views import CartViewSet,CartItemViewSet
from rest_framework.routers import DefaultRouter
router=DefaultRouter()
router.register(r"cart-items",CartItemViewSet)
router.register(r"create-carts",CartViewSet)

urlpatterns = [
    path("",include(router.urls)),
]

