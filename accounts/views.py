from django.shortcuts import render
from .models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.http import JsonResponse
import sentry_sdk
from django.http import JsonResponse


def sentry_test(request):
    raise RuntimeError("SENTRY_TEST_12345")
    
def test_sentry(request):
    data = {}
    value = data["missing_key"]

    return JsonResponse({"value": value})

import sentry_sdk

def test_sentry(request):
    try:
        data = {}
        value = data["missing_key"]
        return JsonResponse({"value": value})

    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise

def test_sentry(request):
    raise Exception("Testing Sentry")

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # authenticate user
        ...
class RegisterView(APIView):

    def post(self,requests):
        email=requests.data["email"]
        password=requests.data["password"]
        serializer=RegisterSerializer(data=requests.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User Registered Successfully"},status=status.HTTP_200_OK)


        return Response({"message":serializer.errors},status=404)


class LoginAPIView(APIView):
    permission_classes=[AllowAny]
    authentication_classes=[]

    def post(self,requests):
        email=requests.data["email"]
        password=requests.data["password"]
        user=authenticate(requests,email=email,password=password)
        print(email,password,user,user.email,user.password,type(user))

        if user is None:
            return Response({"error":"Invalid credentials"},status.HTTP_401_UNAUTHORISED)

        refresh=RefreshToken.for_user(user)
        response = Response({
            "message": "Login successful"
        })

        response.set_cookie(
            key="access_token",
            value=str(refresh.access_token),
            httponly=True,
            secure=False,       # True in production (HTTPS)
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return response

       # print(refresh)

       #return Response({"refresh":str(refresh),"access":str(refresh.access_token)},status=200)




class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
