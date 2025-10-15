
# mpgpro/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static helper

urlpatterns = [
    path('adminmyaryacanaccess/', admin.site.urls),
    path('', include('mpgepmc_core.urls', namespace='mpgepmc_core')), # Include your app's URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)