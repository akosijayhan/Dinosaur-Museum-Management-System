from rest_framework import serializers
from map.models import MapCoordinates


class MapCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapCoordinates
        fields = ['id', 'room', 'room_name', 'floor_level']