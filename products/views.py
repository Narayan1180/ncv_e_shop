from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer,CategorySerializer
from .models import Product,Category
from rest_framework.permissions import (AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, )

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin,CreateModelMixin,UpdateModelMixin,DestroyModelMixin,RetrieveModelMixin
from rest_framework import generics
# Create your views here.
from django.shortcuts import render
from .models import Product
from .permissions import ProductPermission

def home(request):
    products = Product.objects.select_related("category")
    #print(products)
    serializer=ProductSerializer(products,many=True)

    print(serializer.data)

    return render(request, "product/product_page.html", {
        "products": serializer.data,
    })

class ProductViewSets(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAuthenticated,ProductPermission]
    
    def perform_create(self,serializer):
        serializer.save(seller=self.request.user)
    """
    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)


        return render(request,"product/product_page.html",
            {
                "products": serializer.data
            }
        )
    
    def get_permissions(self):

        if self.action in ["list", "retrieve","create"]:
            return [AllowAny()]

        return [IsAdminUser()]
    """

class CategoryViewSets(ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    #serializer_class=CategorySerializers

class ListCreateAPIView(ListModelMixin,CreateModelMixin,GenericAPIView):
    queryset=Product.objects.all()
    #print(queryset)
    serializer_class=ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    
class RetrieveUpdateDestroy(RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,GenericAPIView):
    queryset=Product.objects.all()
    #print(queryset)
    serializer_class=ProductSerializer
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProdList(generics.ListCreateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer

class ProdListUpdDel(generics.RetrieveUpdateDestroyAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer









