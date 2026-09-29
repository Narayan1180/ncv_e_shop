
from django.contrib import admin
from django.urls import path,include
from .views import dump_excel,get_info
from rest_framework.routers import DefaultRouter
router=DefaultRouter()
#router.register(r"cart-items",CartItemViewSet)
#router.register(r"",CartViewSet)

urlpatterns = [
    path("import/",dump_excel),
    path("get_data/",get_info),
   # path("",include(router.urls)),
]

