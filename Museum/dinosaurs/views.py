from accounts.permissions import IsOwnerOrAdmin
from dinosaurs.models import Dinosaur
from dinosaurs.serializers import DinosaurSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication


class DinosaurListCreateView(APIView):
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsAuthenticatedOrReadOnly]
  parser_classes = [MultiPartParser, FormParser]

  def get(self, request):
    dinosaurs = Dinosaur.objects.all().order_by('-id')
    # Pass context={'request': request} so DRF builds full image URLs
    serializer = DinosaurSerializer(
        dinosaurs, many=True, context={'request': request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)

  def post(self, request):
    serializer = DinosaurSerializer(
        data=request.data, context={'request': request}
    )
    if serializer.is_valid():
      serializer.save(created_by=request.user)
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DinosaurDetailView(APIView):
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsOwnerOrAdmin]
  parser_classes = [MultiPartParser, FormParser]

  def get_object(self, pk):
    dino = get_object_or_404(Dinosaur, pk=pk)
    self.check_object_permissions(self.request, dino)
    return dino

  def put(self, request, pk):
    dino = self.get_object(pk)
    serializer = DinosaurSerializer(
        dino, data=request.data, partial=True, context={'request': request}
    )
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk):
    dino = self.get_object(pk)
    dino.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)