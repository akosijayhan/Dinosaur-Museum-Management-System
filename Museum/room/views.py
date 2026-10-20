from accounts.permissions import IsOwnerOrAdmin
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Room
from .serializers import RoomSerializer


class RoomListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user or not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'detail': 'Only administrators can create museum rooms.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            created_by = request.user if request.user.is_authenticated else None
            serializer.save(created_by=created_by)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk, request):
        room = get_object_or_404(Room, pk=pk)
        self.check_object_permissions(request, room)
        return room

    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        serializer = RoomSerializer(room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not request.user or not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'detail': 'Only administrators can update museum rooms.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        room = self.get_object(pk, request)
        serializer = RoomSerializer(
            room, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user or not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'detail': 'Only administrators can delete museum rooms.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        room = self.get_object(pk, request)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)