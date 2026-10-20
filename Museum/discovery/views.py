from accounts.permissions import IsOwnerOrAdmin
from discovery.models import Discovery
from discovery.serializers import DiscoverySerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication


class DiscoveryListCreateView(APIView):
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsAuthenticatedOrReadOnly]

  def get(self, request):
    discoveries = Discovery.objects.all().order_by('-id')
    serializer = DiscoverySerializer(discoveries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def post(self, request):
    if not request.user or not request.user.is_authenticated:
      return Response(
          {'detail': 'Authentication credentials were not provided.'},
          status=status.HTTP_401_UNAUTHORIZED,
      )

    serializer = DiscoverySerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(created_by=request.user)
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscoveryDetailView(APIView):
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsOwnerOrAdmin]

  def get_object(self, pk):
    discovery = get_object_or_404(Discovery, pk=pk)
    self.check_object_permissions(self.request, discovery)
    return discovery

  def get(self, request, pk):
    discovery = self.get_object(pk)
    serializer = DiscoverySerializer(discovery)
    return Response(serializer.data, status=status.HTTP_200_OK)

  def put(self, request, pk):
    discovery = self.get_object(pk)
    serializer = DiscoverySerializer(
        discovery, data=request.data, partial=True
    )
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def delete(self, request, pk):
    discovery = self.get_object(pk)
    discovery.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)