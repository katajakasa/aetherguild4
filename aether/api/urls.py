from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import ForumPostViewSet

app_name = "api"

router = DefaultRouter()
router.register(r"posts", ForumPostViewSet, "forumpost")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
