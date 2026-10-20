from django.urls import path
from map.views import MapDetailView, MapListCreateView

urlpatterns = [
    path('', MapListCreateView.as_view(), name='map-list-create'),
    path('<int:pk>/', MapDetailView.as_view(), name='map-detail'),
]