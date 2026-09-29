from django.shortcuts import render
from .models import Cart,CartItem
from rest_framework.viewsets import ModelViewSet
from .serialisers import CartSerializer,CartItemSerializer
# Create your views here.
from rest_framework.permissions import IsAuthenticated

class CartViewSet(ModelViewSet):
    queryset=Cart.objects.all()
    serializer_class=CartSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class CartItemViewSet(ModelViewSet):
    queryset=CartItem.objects.all()
    serializer_class=CartItemSerializer
    permission_classes=[IsAuthenticated]


    def get_queryset(self):
        c=CartItem.objects.filter(cart__user=self.request.user)
        print("c",c)
        return c

    def perform_create(self, serializer):


        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )

        serializer.save(cart=cart)