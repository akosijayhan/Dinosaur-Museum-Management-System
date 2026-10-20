from django.urls import path
from .views import DiscoveryDetailView, DiscoveryListCreateView

urlpatterns = [
    path('', DiscoveryListCreateView.as_view(), name='discovery-list-create'),
    path('<int:pk>/', DiscoveryDetailView.as_view(), name='discovery-detail'),
]