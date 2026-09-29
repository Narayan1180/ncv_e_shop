from rest_framework import serializers
from .models import Cart,CartItem

class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model=Cart
        fields="__all__"



class CartItemSerializer(serializers.ModelSerializer):
    #cart=CartSerializer(read_only=True)
    cart = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model=CartItem
        fields="__all__"
        #read_only_fields = ["id", "cart"]

