from rest_framework import serializers

from .models import Dinosaur


class DinosaurSerializer(serializers.ModelSerializer):
  created_by = serializers.ReadOnlyField(source='created_by.username')
  image = serializers.ImageField(required=False, allow_null=True)

  class Meta:
    model = Dinosaur
    fields = [
        'id',
        'name',
        'species',
        'period',
        'diet',
        'description',
        'image',
        'room',
        'created_by',
        'created_at',
    ]
    read_only_fields = ['id', 'created_by', 'created_at']