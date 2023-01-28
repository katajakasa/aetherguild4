from django.contrib.auth.models import User
from django.db.models import Exists, OuterRef, Q
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ReadOnlyModelViewSet

from aether.forum.models import ForumPost

from .serializers import ForumPostSerializer


class ForumPostViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ForumPostSerializer

    def get_queryset(self):
        qs = (
            ForumPost.objects.select_related("user", "user__profile")
            .prefetch_related("edits")
            .filter(deleted=False)
            .defer(
                "user__first_name",
                "user__last_name",
                "user__email",
                "user__last_login",
                "user__password",
                "user__username",
                "user__is_active",
            )
        )

        user = self.request.user
        if user and user.is_authenticated:
            subq = (
                User.objects.filter(pk=user.id)
                .filter(
                    Q(is_superuser=True)
                    | Q(groups__permissions__codename=OuterRef("thread__board__read_perm__codename"))
                )
                .values("pk")
            )
            qs = qs.annotate(can_read=Exists(subq)).filter(
                Q(thread__board__read_perm=None) | Q(can_read=True)
            )
        else:
            qs = qs.filter(thread__board__read_perm=None)

        return qs
