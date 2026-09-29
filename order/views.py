from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Order,OrderItem
from .serializers import OrderItemSerializer,OrderSerializer# Create your views here.
from rest_framework.views import APIView
from cart.models import Cart,CartItem
from products.models import Product
from rest_framework.response import Response
from rest_framework import status
from .tasks import send_order_email
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from django.urls import reverse

import razorpay

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.contrib.sessions.models import Session
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class OrderItemView(ModelViewSet):
    queryset=OrderItem.objects.all()
    serializer_class=OrderItemSerializer
    def get_queryset(self):

        return OrderItem.objects.filter(order__user=self.request.user)


class OrderView(ModelViewSet):
    queryset=Order.objects.all()
    serializer_class=OrderSerializer

    def get_queryset(self):

        return Order.objects.filter(user=self.request.user)


from .services import ProcessOrder,RazorpayGateway

import razorpay.errors
import requests.exceptions

class CheckOutView(APIView):

    def post(self,request):
        user=request.user
        print(user)

        try:
            order, razorpay_order = ProcessOrder(user).create_order()

        except razorpay.errors.BadRequestError as e:
            error_message = str(e).lower()
            if "too many request" in error_message:
                return Response({"error": "Payment gateway busy, please retry shortly"}, status=429)
            return Response({"error": "Invalid payment request", "detail": str(e)}, status=400)

        except razorpay.errors.ServerError as e:
            return Response({"error": "Payment gateway temporarily unavailable"}, status=503)

        except razorpay.errors.GatewayError as e:
            return Response({"error": "Payment gateway error, please retry"}, status=503)

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            return Response({"error": "Payment gateway unreachable, please retry"}, status=503)

        except OperationalError:
            return Response({"error": "Server busy, please retry"}, status=503)

        except Exception as e:
            #logger.exception("Unexpected error creating order")
            return Response({"error": "Something went wrong"}, status=500)      
                #print("SESSION DATA:", dict(request.session))
                    #print("SESSION KEY:", request.session.session_key)
                    #print("MODIFIED:", request.session.modified)
        serializer=OrderSerializer(order)

        return Response({"data":serializer.data,"payment_url": f"/payment/{order.id}/"},status=200)



# views.py

from .tasks import send_notification,create_mail_notification,create_msg_notifications


class VerifyPaymentView(APIView):

    #authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        # 1. Get order belonging to authenticated user
        print(request.user)
        order = get_object_or_404(Order, id=order_id, user=request.user )

        # 2. Get Razorpay payment data
        payment_id = request.data.get("razorpay_payment_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        signature = request.data.get("razorpay_signature")

        if not all([ payment_id, razorpay_order_id, signature ]):
            return Response( { "success": False, "error": "Missing payment data" }, status=400 )
        # 3. Make sure Razorpay order belongs to our DB order
        if razorpay_order_id != order.razorpay_order_id:
            return Response( { "success": False, "error": "Invalid order" }, status=400 )
        print("hi")
        try:

            # 4. Verify Razorpay signature
            razor_conn = RazorpayGateway()

            razor_conn.verify_payment_signature({ "razorpay_order_id": razorpay_order_id, "razorpay_payment_id": payment_id, "razorpay_signature": signature, })
            print("inside")
            # 5. Atomic DB update
            with transaction.atomic():

                order = Order.objects.select_for_update().get( id=order_id )
                # 6. Idempotency
                if order.payment_status != "paid":

                    order.status = "confirmed"
                    order.payment_status = "paid"
                    order.razorpay_payment_id = payment_id

                    order.save( update_fields=[ "payment_status", "status", "razorpay_payment_id", ] )

            # 7. Send email asynchronously
            try:
                result = send_order_email.delay( order.id, order.user.email )
                send_notification.delay_on_commit(create_mail_notification(order.user,order))
                send_notification.delay_on_commit(create_msg_notifications(order.user,order))
                #r=send_sms("+916283952017",f"order confirmed")
                #r = send_sms( "+916283952017", "Reminder: Appt Tue Oct 29, 3:00 PM. Reply C to confirm or R to reschedule. Test message from Twilio." )
                #print(r)


                print("Celery task ID:", result.id)

            except Exception as e:
                print("Celery error:", e)

            # 8. Return API response
            return Response(
                {
                    "success": True,
                    "message": "Payment verified successfully",
                    "redirect_url": reverse(
                        "order-detail",
                        kwargs={"order_id": order.id}
                    )
                },
                status=200
            )

        except Exception as e:

            print(
                "Payment verification error:",
                type(e).__name__,
                str(e)
            )

            return Response(
                {
                    "success": False,
                    "error": "Payment verification failed"
                },
                status=400
            )






class OrderDetailView(APIView):
    #authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        print(request.user)

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )
        return render( request, "order/order_detail.html", { "order": order } )


def order_detail(request, order_id):
    print("USER:", request.user)
    print("USER ID:", request.user.id)
    print("AUTHENTICATED:", request.user.is_authenticated)


    print(request.user)
    order = get_object_or_404( Order, id=order_id,user=request.user )
    print(order)
    return render( request, "order/order_detail.html", { "order": order } )




from .twilio_mg import send_sms


class PlaceOrderView(APIView):

    def post(self,request):

        order=Order.objects.create(user=self.request.user,total_amount=0)

        cart_item=CartItem.objects.filter(cart__user=self.request.user)

        if not cart_item:
            order.delete()
            return Response({"message":"order cannot be placed to place order add item to the cart"},status=400)


        for item in cart_item:
            print(item.product.id,item.product.price)
            product=Product.objects.get(id=item.product.id)
            print(product,order,order.id)
            quantity=item.quantity

            OrderItem.objects.create(order=order,product=product,quantity=quantity,price=quantity*product.price)

        
        order.total_amount=sum(item.price for item in OrderItem.objects.filter(order=order))
        order.save()
        serializer=OrderSerializer(order)
        #cart=Cart.objects.get(user=self.request.user)
        #cart.delete()
        #print(cart)
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_SECRET
            )
        )

        razorpay_order = client.order.create({
            "amount": int(order.total_amount/1000),       # ₹100
            "currency": "INR",
            "receipt": str(order.id)
        })
        
        request.session["razorpay_order_id"] = razorpay_order["id"]


        return Response({
            "order_id": order.id,
            "razorpay_order_id": razorpay_order["id"],
            "payment_url": f"/payment/{order.id}/"
        })
        cart_item.delete()
        print(self.request.user.email)
        result=send_order_email.delay(order.id,self.request.user.email)
        print(result.id)
        return Response({"data":serializer.data},status=200)

def payment_page(request, order_id):

    print(request.user, order_id)

    order = get_object_or_404(
        Order,
        id=order_id,
    )

    print(order)

    razorpay_order_id = request.session.get("razorpay_order_id")
    razorpay_order_id = order.razorpay_order_id


    print("Razorpay Order ID:", razorpay_order_id)
    print("RAZORPAY KEY:", settings.RAZORPAY_KEY_ID)
    print("RAZORPAY ORDER:", razorpay_order_id)
    print("AMOUNT:", order.total_amount)

    return render(
        request,
        "order/payment.html",
        {
            "order": order,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        }
    )


