from dinosaurs.views import DinosaurDetailView, DinosaurListCreateView
from django.urls import path

urlpatterns = [
    path('', DinosaurListCreateView.as_view(), name='dinosaur-list-create'),
    path('<int:pk>/', DinosaurDetailView.as_view(), name='dinosaur-detail'),
]