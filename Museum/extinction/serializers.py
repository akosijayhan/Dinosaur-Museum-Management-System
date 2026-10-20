from rest_framework import serializers
from .models import ExtinctionEvent


class ExtinctionEventSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ExtinctionEvent
        fields = [
            'id',
            'name',
            'period',
            'estimated_date',
            'cause',
            'description',
            'dinosaur',
            'image',
            'created_by',
            'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']