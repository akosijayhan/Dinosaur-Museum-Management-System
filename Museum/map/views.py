from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from map.models import MapCoordinates
from map.serializers import MapCoordinatesSerializer


class MapListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # LIST ALL MAP PINS
    def get(self, request):
        maps = MapCoordinates.objects.all()
        serializer = MapCoordinatesSerializer(maps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # CREATE NEW MAP PIN
    def post(self, request):
        serializer = MapCoordinatesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MapDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return MapCoordinates.objects.get(pk=pk)
        except MapCoordinates.DoesNotExist:
            return None

    # GET MAP PIN DETAILS
    def get(self, request, pk):
        map_obj = self.get_object(pk)
        if not map_obj:
            return Response(
                {'message': 'Map entry not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MapCoordinatesSerializer(map_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # UPDATE MAP PIN
    def put(self, request, pk):
        map_obj = self.get_object(pk)
        if not map_obj:
            return Response(
                {'message': 'Map entry not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MapCoordinatesSerializer(
            map_obj, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE MAP PIN
    def delete(self, request, pk):
        map_obj = self.get_object(pk)
        if not map_obj:
            return Response(
                {'message': 'Map entry not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        map_obj.delete()
        return Response(
            {'message': 'Map entry deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )