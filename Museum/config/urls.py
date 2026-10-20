from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/room/', include('room.urls')),
    path('api/dinosaurs/', include('dinosaurs.urls')),
    path('api/discovery/', include('discovery.urls')),
    path('api/extinction/', include('extinction.urls')),
    path('api/map/', include('map.urls')),
]

# Serves uploaded media files (images) during local development
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)