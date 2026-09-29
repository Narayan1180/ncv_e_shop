from ..models import Order,OrderItem
from cart.models import Cart,CartItem
from products.models import Product
from .RazorPayService import RazorpayGateway
import razorpay.errors
from razorpay.errors import BadRequestError  # add this import at the top of the file
from rest_framework.response import Response
from django.conf import settings
import uuid
class ProcessOrder:


    def __init__(self,user):

        print("insider orderservice",user)

        self.user=user

    def create_order(self):
        

        print(self.user)
        order=Order.objects.create(user=self.user,total_amount=0)

        cart=self.get_cart()

        cart_item=self.get_cart_items(cart)

        create_cart_items=self.create_cart_items(cart_item,order)
        #print(cart_item)
        
        
        print([oi.price for oi in OrderItem.objects.filter(order=order)])
        order.total_amount=sum([oi.price for oi in OrderItem.objects.filter(order=order)])
        print(order.total_amount)
        #order.save()
        razorpay=RazorpayGateway().create_payment_order(order)
            
        order.razorpay_order_id = razorpay["id"]

        order.save()


        #cart_item.delete()

        return (order,razorpay)



    def get_cart(self):
        return Cart.objects.get(user=self.user)

    def get_cart_items(self,cart):
        return CartItem.objects.filter(cart=cart)

    def create_cart_items(self,cart_item,order):

        for item in cart_item:
            print(item.product.price)
            product=Product.objects.get(id=item.product.id)

            order_item=OrderItem(order=order,product=product,quantity=item.quantity,price=product.price*item.quantity)
            order_item.save()




    