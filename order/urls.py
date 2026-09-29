
from django.contrib import admin
from django.urls import path,include
from .views import OrderItemView,OrderView,PlaceOrderView,payment_page,CheckOutView,VerifyPaymentView,order_detail,OrderDetailView
from rest_framework.routers import DefaultRouter
router=DefaultRouter()
router.register(r"order-list",OrderView)
router.register(r"order-items",OrderItemView)

urlpatterns = [
    path("payment/<int:order_id>/",payment_page,name="payment_page"),
    path("place-order/",PlaceOrderView.as_view()),
    path("checkout/",CheckOutView.as_view()),
    
    path( "payment/<int:order_id>/verify/", VerifyPaymentView.as_view(), name="verify_payment", ),

    path( "order_detail/<int:order_id>/", OrderDetailView.as_view(), name="order-detail" ),

    path("",include(router.urls)),

    
]

