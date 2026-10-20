from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'floor', 'description', 'image', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']