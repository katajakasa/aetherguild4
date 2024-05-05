from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("aether.main_site.urls", namespace="main_site")),
    path("gallery/", include("aether.gallery.urls", namespace="gallery")),
    path("forum/", include("aether.forum.urls", namespace="forum")),
    path("api/v1/", include("aether.api.urls", namespace="api")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
