from django.urls import path
from .views import ExtinctionListCreateView, ExtinctionDetailView

urlpatterns = [
    path('', ExtinctionListCreateView.as_view(), name='extinction-list-create'),
    path('<int:pk>/', ExtinctionDetailView.as_view(), name='extinction-detail'),
]