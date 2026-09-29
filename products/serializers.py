from .models import Product,Category
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField( queryset=Category.objects.filter(is_active=True) )

 
    class Meta:
        model=Product
        fields="__all__"

    """
    def create(self,validated_data):
        category_data=validated_data.pop("category",[])
        category, created = Category.objects.get_or_create(name=category_data["name"])

        #print(category,created)

        return Product.objects.create(category=category,**validated_data)

    def update(self,instance,validated_data):
        category_data=validated_data.pop("category",None)
        if category_data:
            category, created = Category.objects.get_or_create(name=category_data["name"])
            instance.category=category

        
        for attr, value in validated_data.items():
            #print(attr,value)
            setattr(instance, attr, value)


        #instance.name=validated_data.get("name",instance.name)
        #instance.product_image=validated_data.get("product_image",instance.product_image)
        #instance.price=validated_data.get("price",instance.price)
        #instance.description=validated_data.get("description",instance.description)

        #instance.discount=validated_data.get("discount",instance.discount)
        instance.save()



        
        print(validated_data,instance)

        return instance

    """
