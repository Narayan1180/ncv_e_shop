
from django.contrib import admin
from django.urls import path,include
from .views import ProductViewSets,CategoryViewSets,ListCreateAPIView,RetrieveUpdateDestroy,ProdList,ProdListUpdDel,home
from rest_framework.routers import DefaultRouter
router=DefaultRouter()
router.register(r"category",CategoryViewSets)
router.register(r"",ProductViewSets)

urlpatterns = [
    path("api/",ProdList.as_view()),
    path("api/<int:pk>",ProdListUpdDel.as_view()),
    path("api-list/",ListCreateAPIView.as_view()),
    path("api-list/<int:pk>/",RetrieveUpdateDestroy.as_view()),
    path("home_page",home),
    path("",include(router.urls)),

    
]

