from rest_framework import serializers
from .models import Accounts


class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True)

  class Meta:
    model = Accounts
    fields = ['id', 'username', 'password']

  def create(self, validated_data):
    return Accounts.objects.create_user(
        username=validated_data['username'],
        password=validated_data['password'],
    )