from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Accounts
from .serializers import RegisterSerializer


# 1. Custom Serializer to append extra fields to the JWT response
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

  def validate(self, attrs):
    data = super().validate(attrs)
    data['username'] = self.user.username
    data['is_staff'] = self.user.is_staff
    data['is_superuser'] = self.user.is_superuser
    return data


# 2. Custom Token Obtain View
class CustomTokenObtainPairView(TokenObtainPairView):
  serializer_class = CustomTokenObtainPairSerializer


# 3. Registration View
class RegisterView(APIView):
  permission_classes = [AllowAny]

  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
          {'message': 'Account created successfully.'},
          status=status.HTTP_201_CREATED,
      )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)