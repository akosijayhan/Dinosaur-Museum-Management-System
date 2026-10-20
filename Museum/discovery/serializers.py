from rest_framework import serializers
from .models import Discovery


class DiscoverySerializer(serializers.ModelSerializer):
  # Return username string in GET responses for frontend permission check
  created_by = serializers.ReadOnlyField(source='created_by.username')

  class Meta:
    model = Discovery
    fields = [
        'id',
        'dinosaur',
        'location',
        'discovery_date',
        'discovered_by',
        'description',
        'created_by',
        'created_at',
    ]
    read_only_fields = ['id', 'created_by', 'created_at']