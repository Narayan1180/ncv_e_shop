from .models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=["email","password"]

    def create(self,validated_data):
        return User.objects.create_user(email=validated_data["email"],password=validated_data["password"])

    

